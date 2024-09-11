import argparse
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.auth import HTTPDigestAuth

# Variable pour stocker le port trouvé après le premier scan
port_scanned = None

# Expand IP range
def expand_ip_range(ip_range):
    ip_list = []
    match = re.match(r'^(\d+\.\d+\.\d+\.)\{([\d,]+)\}$', ip_range)
    
    if match:
        prefix = match.group(1)
        numbers = match.group(2).split(',')
        
        for num in numbers:
            ip_list.append(prefix + num)
    
    return ip_list

def scan_ports(target_ip):
    open_ports = []
    command = ['nmap', target_ip, '-p', '1-65535', '--open']  # Ajouter les ports que vous souhaitez tester
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode == 0:
        lines = output.decode('utf-8').split('\n')
        for line in lines:
            if '/tcp' in line and 'open' in line:
                port = int(line.split('/')[0])
                open_ports.append(port)
        return open_ports
    else:
        print(f"Erreur lors de l'exécution de la commande Nmap: {error.decode('utf-8')}")
        return []

# Check if port is HTTP
def is_http_port(session, camera_ip, username, password, port):
    url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode[1].ExtraFormat[0]"
    try:
        r = session.get(url, stream=True, auth=HTTPDigestAuth(username, password), timeout=5)
        r.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False
port_scanned = None
nb_cam_scanned = None
def numberCam(session, camera_ip, username, password):
    global port_scanned, nb_cam_scanned
    print(f"Appel de numberCam pour IP: {camera_ip}, port_scanned: {port_scanned}, nb_cam_scanned: {nb_cam_scanned}")
    
    # Si le port et le nombre de caméras ont déjà été scannés, les utiliser
    if port_scanned and nb_cam_scanned:
        print(f"Utilisation du port scanné: {port_scanned}, et du nombre de caméras scanné: {nb_cam_scanned}")
        return [nb_cam_scanned, port_scanned]
    
    # Essai du port par défaut: 80
    print("Essai du port par défaut: 80")
    port = 80
    url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Ptz"
    
    try:
        r = session.get(url, stream=True, auth=HTTPDigestAuth(username, password), timeout=5)
        print(f"Réponse du port 80: {r.status_code}")
        if r.status_code == 200:
            matches = re.findall(r'table\.Ptz\[(\d+)\]', r.text)
            if matches:
                dernier_chiffre = int(matches[-1])
                port_scanned = str(port)  # Stocker le port scanné
                nb_cam_scanned = dernier_chiffre + 1  # Stocker le nombre de caméras scannées
                print(f"Port 80 valide, retour: {nb_cam_scanned}, port: {port}")
                return [nb_cam_scanned, str(port)]
        else:
            print(f"Port 80 non valide, réponse: {r.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion sur le port {port}: {str(e)}, passage au scan des autres ports.")
    
    # Si le port 80 échoue, scanner les autres ports
    open_ports = scan_ports(camera_ip)
    print(f"Ports ouverts trouvés: {open_ports}")
    for port in open_ports:
        print(f"Essai du port {port}")
        if is_http_port(session, camera_ip, username, password, port):
            port_scanned = str(port)  # Stocker le port scanné
            url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Ptz"
            try:
                r = session.get(url, stream=True, auth=HTTPDigestAuth(username, password), timeout=5)
                print(f"Réponse du port {port}: {r.status_code}")
                if r.status_code == 200:
                    matches = re.findall(r'table\.Ptz\[(\d+)\]', r.text)
                    print(f"Matches trouvés sur le port {port}: {matches}")
                    if matches:
                        dernier_chiffre = int(matches[-1])
                        nb_cam_scanned = dernier_chiffre + 1  # Stocker le nombre de caméras scannées
                        print(f"Port {port} valide, retour: {nb_cam_scanned}, port: {port}")
                        return [nb_cam_scanned, str(port)]
                    else:
                        nb_cam_scanned = 30  # Par défaut, 30 caméras si rien n'est trouvé
                        print(f"Aucune caméra trouvée sur le port {port}, retour par défaut.")
                        return [nb_cam_scanned, str(port)]
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la tentative avec le port {port}: {str(e)}")
    
    # Si aucun port ne fonctionne
    print("Aucun port valide trouvé, retour par défaut [1, None].")
    return [1, None]

# Get camera info
def getinfoCam(session, camera_ip, username, password, channel_id, cam):
    global port_scanned
    number = numberCam(session, camera_ip, username, password)
    port = port_scanned  # Utiliser le port scanné
    nbCam = int(number[0])

    # Si 'cam' est défini à 'yes', on traite toutes les caméras à moins qu'un canal spécifique soit demandé
    if cam == "yes" or channel_id in ["all_main", "all_sub"]:
        print(f"Traitement de {nbCam} caméras.")  # Affiche combien de caméras sont traitées
    else:
        print(f"Traitement d'une seule caméra, canal {channel_id}")
        nbCam = 1  # Limite à une seule caméra si un canal spécifique est demandé

    # Récupérer les configurations d'encodage pour toutes les caméras d'un coup
    url_encode = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode"
    url_motion = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=MotionDetect"

    r_encode = session.get(url_encode, stream=True, auth=HTTPDigestAuth(username, password))
    r_motion = session.get(url_motion, stream=True, auth=HTTPDigestAuth(username, password))

    if r_encode.status_code == 200 and r_motion.status_code == 200:
        encode_text = r_encode.text.split('\n')
        motion_text = r_motion.text.split('\n')
        
        # Parcourir les caméras en traitant les données récupérées en une fois
        results = {}
        for x in range(nbCam):  # Toujours parcourir jusqu'à nbCam, qui peut être 1 ou plus
            try:
                format_type = "ExtraFormat[0]" if channel_id == "all_sub" else "MainFormat[0]"

                # Récupérer les informations de la caméra dans la réponse encode
                compression_types = next(line.split('=')[1].strip() for line in encode_text if f'table.Encode[{x}].{format_type}.Video.Compression' in line)
                resolution_types = next(line.split('=')[1].strip() for line in encode_text if f'table.Encode[{x}].{format_type}.Video.resolution' in line)
                fps_types = next(line.split('=')[1].strip() for line in encode_text if f'table.Encode[{x}].{format_type}.Video.FPS' in line)
                bitrate_types = next(line.split('=')[1].strip() for line in encode_text if f'table.Encode[{x}].{format_type}.Video.BitRate' in line)
                bitrate_control = next(line.split('=')[1].strip() for line in encode_text if f'table.Encode[{x}].{format_type}.Video.BitRateControl' in line)

                # Récupérer les informations de détection de mouvement dans la réponse motion
                motion_d = next(line.split('=')[1].strip() for line in motion_text if f'table.MotionDetect[{x}].Enable' in line)

                camF = str(x + 1) + "02" if channel_id == "all_sub" else str(x + 1) + "01"
                results[x] = (x+1,compression_types, resolution_types, fps_types, bitrate_types, camF, bitrate_control, motion_d)
            except StopIteration:
                print(f"Erreur lors de la lecture des paramètres pour la caméra {x + 1}.")
                pass

        # Afficher les résultats
        for x in sorted(results):
            print_results_cam(*results[x])
    else:
        print(f"Erreur lors de la récupération des informations pour {camera_ip} : {r_encode.status_code}, {r_motion.status_code}")


# Print results
def print_results_cam(camera_number,compression_types, resolution_types, fps_types, bitrate_types, channel, bitratecontrol, motion_d):
    print(camera_number)
    print('ID Channel :', channel)
    print('Resolution : ', resolution_types)
    print('Type bande passante : ', bitratecontrol)
    if int(float(fps_types)) == 0:
        print('Image par seconde : MAX fps')
    else:
        print('Image par seconde : ', int(float(fps_types)), 'fps')
    print('Debit binaire max : ', bitrate_types.replace(",", "-"))
    print('Encodage vidéo : ', compression_types)
    print('Motion Detect : ', motion_d)
    print("-----------")

# Get all settings
def getAllSettings(session, camera_ip, username, password):
    global port_scanned
    number = numberCam(session, camera_ip, username, password)
    port = port_scanned  # Utiliser le port scanné
    url = f"http://{camera_ip}:{port}/cgi-bin/encode.cgi?action=getConfigCaps"
    url_user = f"http://{camera_ip}:{port}/cgi-bin/userManager.cgi?action=getUserInfoAll"
    
    r = session.get(url, stream=True, auth=HTTPDigestAuth(username, password))
    r_user = session.get(url_user, stream=True, auth=HTTPDigestAuth(username, password))
    
    if r.status_code == 200 and r_user.status_code == 200:
        print(f"Pour IP {camera_ip}")
        text_user = r_user.text
        patterns = {
            'names': re.compile(r"users\[(\d+)\]\.Name=(\w+)"),
            'groups': re.compile(r"users\[(\d+)\]\.Group=(\w+)"),
            'authorities': re.compile(r"users\[(\d+)\]\.AuthorityList\[\d+\]=(\w+)")
        }
        data = {key: {} for key in patterns.keys()}
        for key, pattern in patterns.items():
            for match in pattern.finditer(text_user):
                user_index, value = match.groups()
                if key == 'authorities':
                    data[key].setdefault(int(user_index), []).append(value)
                else:
                    data[key][int(user_index)] = value
        
        for user_index in data['names'].keys():
            print(f"User {user_index}")
            print(f"Name: {data['names'][user_index]}")
            print(f"Group: {data['groups'][user_index]}")
            print(f"Droit: {data['authorities'][user_index]}")
            print()

        formats = ['MainFormat[0]', 'ExtraFormat[0]']
        params = ['CompressionTypes', 'ResolutionTypes', 'FPSMax', 'BitRateOptions']
        
        def extract_and_print_params(text, format_type):
            try:
                for param in params:
                    target_line = next(line for line in text.split('\n') if f'caps[0].{format_type}.Video.{param}' in line)
                    value = target_line.split('=')[1].strip()
                    print(f"{param.replace('Types', '').replace('Options', '')} : {value}")
                print("-----------")
            except StopIteration:
                print(f"Erreur d'extraction pour {format_type}")
        print("// Flux primaire //")
        extract_and_print_params(r.text, 'MainFormat[0]')
        print("// Flux secondaire //")
        extract_and_print_params(r.text, 'ExtraFormat[0]')

# Set resolution
def setResolution(session, camera_ip, username, password, channel_id, resolution, cam):
    global port_scanned
    number = numberCam(session, camera_ip, username, password)
    port = port_scanned  # Utiliser le port scanné
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1
    results = {}

    def set_resolution_for_camera(camera_index, format_type):
        resolution_com = f"Encode[{camera_index}].{format_type}.Video.resolution"
        url_resolution = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}={resolution}"
        r = session.put(url_resolution, stream=True, auth=HTTPDigestAuth(username, password))
        if r.status_code == 200:
            results[camera_index] = f"Resolution pour camera {camera_index + 1} mise à {resolution}"
        elif r.status_code == 400 and format_type == "ExtraFormat[0]":
            url_resolution = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}=704x576"
            r = session.put(url_resolution, stream=True, auth=HTTPDigestAuth(username, password))
            if r.status_code == 200:
                results[camera_index] = f"Resolution pour camera {camera_index + 1} mise à 704x576"
            else:
                results[camera_index] = f"Erreur : {r.status_code} - {r.text}"
        else:
            results[camera_index] = f"Erreur : {r.status_code} - {r.text}"

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        if "all" in channel_id.lower():
            for x in range(nbCam):
                if "sub" in channel_id.lower():
                    futures.append(executor.submit(set_resolution_for_camera, x, "ExtraFormat[0]"))
                elif "main" in channel_id.lower():
                    futures.append(executor.submit(set_resolution_for_camera, x, "MainFormat[0]"))
        else:
            channel_index = int(channel_id) - 1
            futures.append(executor.submit(set_resolution_for_camera, channel_index, "ExtraFormat[0]"))
        for future in as_completed(futures):
            future.result()
    
    for x in sorted(results):
        print(results[x])

# Set FPS
def setFps(session, camera_ip, username, password, channel_id, fps, cam, max_retries=3):
    number = numberCam(session, camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1
    results = {}

    def set_fps_for_camera(camera_index, format_type):
        fps_cam = f"Encode[{camera_index}].{format_type}.Video.FPS"
        url_fps = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{fps_cam}={fps}"
        for attempt in range(max_retries):
            r = session.put(url_fps, stream=True, auth=HTTPDigestAuth(username, password))
            if r.status_code == 200:
                results[camera_index] = f"FPS pour camera {camera_index + 1} mise à {fps}"
                break
            elif r.status_code == 400:
                results[camera_index] = "Pas bon format !"
                break
            else:
                if attempt < max_retries - 1:
                    print(f"Retrying for camera {camera_index + 1}...")
                else:
                    results[camera_index] = f"Erreur : {r.status_code} - {r.text}"

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        if "all" in channel_id.lower():
            for x in range(nbCam):
                if "sub" in channel_id.lower():
                    futures.append(executor.submit(set_fps_for_camera, x, "ExtraFormat[0]"))
                elif "main" in channel_id.lower():
                    futures.append(executor.submit(set_fps_for_camera, x, "MainFormat[0]"))
        else:
            channel_index = int(channel_id) - 1
            futures.append(executor.submit(set_fps_for_camera, channel_index, "ExtraFormat[0]"))
        for future in as_completed(futures):
            future.result()

    for x in sorted(results):
        print(results[x])


# Set Bitrate
def setBitrate(session, camera_ip, username, password, channel_id, bitrate, cam):
    number = numberCam(session, camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1
    results = {}

    def set_bitrate_for_camera(camera_index, format_type):
        bitrate_cam = f"Encode[{camera_index}].{format_type}.Video.BitRate"
        url_bitrate = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{bitrate_cam}={bitrate}"
        r = session.put(url_bitrate, stream=True, auth=HTTPDigestAuth(username, password))
        if r.status_code == 200:
            results[camera_index] = f"BitRate pour camera {camera_index + 1} mise à {bitrate}"
        elif r.status_code == 400:
            results[camera_index] = "Pas bon format !"
        else:
            results[camera_index] = f"Erreur : {r.status_code} - {r.text}"

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        if "all" in channel_id.lower():
            for x in range(nbCam):
                if "sub" in channel_id.lower():
                    futures.append(executor.submit(set_bitrate_for_camera, x, "ExtraFormat[0]"))
                elif "main" in channel_id.lower():
                    futures.append(executor.submit(set_bitrate_for_camera, x, "MainFormat[0]"))
        else:
            channel_index = int(channel_id) - 1
            futures.append(executor.submit(set_bitrate_for_camera, channel_index, "ExtraFormat[0]"))
        for future in as_completed(futures):
            future.result()
    
    for x in sorted(results):
        print(results[x])

# Set Compression
def setCompression(session, camera_ip, username, password, channel_id, compression, cam):
    number = numberCam(session, camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1
    results = {}

    def set_compression_for_camera(camera_index, format_type):
        compression_cam = f"Encode[{camera_index}].{format_type}.Video.Compression"
        compression_cam2 = f"Encode[{camera_index}].{format_type}.Video.Profile=Main"
        url_compression = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam}={compression}"
        url_compression_main = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam2}"
        r = session.put(url_compression, stream=True, auth=HTTPDigestAuth(username, password))
        r2 = session.put(url_compression_main, stream=True, auth=HTTPDigestAuth(username, password))
        if r.status_code == 200:
            results[camera_index] = f"Compression pour camera {camera_index + 1} mise à {compression}"
        elif r.status_code == 400:
            results[camera_index] = "Pas bon format !"
        else:
            results[camera_index] = f"Erreur : {r.status_code} - {r.text}"

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        if "all" in channel_id.lower():
            for x in range(nbCam):
                if "sub" in channel_id.lower():
                    futures.append(executor.submit(set_compression_for_camera, x, "ExtraFormat[0]"))
                elif "main" in channel_id.lower():
                    futures.append(executor.submit(set_compression_for_camera, x, "MainFormat[0]"))
        else:
            channel_index = int(channel_id) - 1
            futures.append(executor.submit(set_compression_for_camera, channel_index, "ExtraFormat[0]"))
        for future in as_completed(futures):
            future.result()
    
    for x in sorted(results):
        print(results[x])

# Set Bitrate Control
def setBitrateControl(session, camera_ip, username, password, channel_id, Bcontrole, cam):
    number = numberCam(session, camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1
    results = {}

    def set_bitrate_control_for_camera(camera_index, format_type):
        bcontrole = f"Encode[{camera_index}].{format_type}.Video.BitRateControl"
        url_bcontrole = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{bcontrole}={Bcontrole}"
        r = session.put(url_bcontrole, stream=True, auth=HTTPDigestAuth(username, password))
        if r.status_code == 200:
            results[camera_index] = f"BitRate Control pour camera {camera_index + 1} mis à {Bcontrole}"
        elif r.status_code == 400:
            results[camera_index] = "Pas bon format !"
        else:
            results[camera_index] = f"Erreur : {r.status_code} - {r.text}"

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        if "all" in channel_id.lower():
            for x in range(nbCam):
                if "sub" in channel_id.lower():
                    futures.append(executor.submit(set_bitrate_control_for_camera, x, "ExtraFormat[0]"))
                elif "main" in channel_id.lower():
                    futures.append(executor.submit(set_bitrate_control_for_camera, x, "MainFormat[0]"))
        else:
            channel_index = int(channel_id) - 1
            futures.append(executor.submit(set_bitrate_control_for_camera, channel_index, "ExtraFormat[0]"))
        for future in as_completed(futures):
            future.result()
    
    for x in sorted(results):
        print(results[x])

# Set Motion Detection
def setDetection(session, camera_ip, username, password, channel_id, motionDetect, cam):
    motionDetect = motionDetect.lower()
    number = numberCam(session, camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1
    results = {}

    def set_motion_detection(camera_index):
        url_detection = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&MotionDetect[{camera_index}].Enable={motionDetect}"
        r = session.put(url_detection, stream=True, auth=HTTPDigestAuth(username, password))
        if r.status_code == 200:
            results[camera_index] = f"Detection mouvement pour camera {camera_index + 1} mise à {motionDetect}"
        elif r.status_code == 400:
            results[camera_index] = "Pas bon format !"
        else:
            results[camera_index] = f"Erreur : {r.status_code} - {r.text}"

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        if "all" in channel_id:
            for x in range(nbCam):
                futures.append(executor.submit(set_motion_detection, x))
        else:
            channel_index = int(channel_id) - 1
            futures.append(executor.submit(set_motion_detection, channel_index))
        for future in as_completed(futures):
            future.result()
    
    for x in sorted(results):
        print(results[x])

# Set Encryption
def setEncrypt(session, camera_ip, username, password):
    url_encrypt = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.wlan0.Enable=true"
    url_encrypt2 = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.wlan0.KeyFlag=true"
    url_encrypt3 = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.wlan0.Encryption=On"
    url_encrypt4 = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=getConfig&name=WLan"
    url_encrypt5 = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.eth2.Encryption=On"
    session.put(url_encrypt, stream=True, auth=HTTPDigestAuth(username, password))
    session.put(url_encrypt2, stream=True, auth=HTTPDigestAuth(username, password))
    session.put(url_encrypt3, stream=True, auth=HTTPDigestAuth(username, password))
    r4 = session.get(url_encrypt4, stream=True, auth=HTTPDigestAuth(username, password))
    if r4.status_code == 200:
        print(r4.text)

# Set Time
def setTime(session, camera_ip, username, password, country):
    number = numberCam(session, camera_ip, username, password)
    port = number[1]
    auth = HTTPDigestAuth(username, password)
    url_before = f"http://{camera_ip}:{port}/cgi-bin/global.cgi?action=getCurrentTime"
    response_before = session.get(url_before, auth=auth, timeout=5)
    print('Time before change :')
    print(response_before.text)
    local_now_string = get_country_time(country)
    url_time = f"http://{camera_ip}:{port}/cgi-bin/global.cgi?action=setCurrentTime&time=" + local_now_string
    response_time = session.post(url_time, auth=auth, timeout=5)
    if response_time.status_code == 200:
        print('Time change successful!')
    response_before = session.get(url_before, auth=auth, timeout=5)
    print('New Time :')
    print(response_before.text)

# Reboot DVR
def reboot_dvr(session, camera_ip, username, password):
    number = numberCam(session, camera_ip, username, password)
    port = number[1]
    auth = HTTPDigestAuth(username, password)
    url_reboot = f"http://{camera_ip}:{port}/cgi-bin/magicBox.cgi?action=reboot"
    response_reboot = session.get(url_reboot, auth=auth, timeout=5)
    if response_reboot.status_code == 200:
        print('The device was successfully restarted.')

# Execute actions
def execute_actions(session, ip, args, cam):
    if args.app:
        getinfoCam(session, ip, args.u, args.p, "all_main", cam)
        getinfoCam(session, ip, args.u, args.p, "all_sub", cam)
        return
    # Si args.ch est spécifié, vérifier si l'utilisateur veut un seul canal ou toutes les caméras
    channel_id = args.ch if args.ch else "all_main"
    print("debut")
    if args.r:
        setResolution(session, ip, args.u, args.p, channel_id, args.r, cam)
    if args.f:
        setFps(session, ip, args.u, args.p, channel_id, args.f, cam)
    if args.b:
        setBitrate(session, ip, args.u, args.p, channel_id, args.b, cam)
    if args.c:
        setCompression(session, ip, args.u, args.p, channel_id, args.c, cam)
    if args.m:
        setDetection(session, ip, args.u, args.p, channel_id, args.m, cam)
    if args.bc:
        setBitrateControl(session, ip, args.u, args.p, channel_id, args.bc, cam)
    if args.ch and not any([args.r, args.f, args.b, args.c, args.m, args.bc]):
        getinfoCam(session, ip, args.u, args.p, channel_id, cam)
    if not any([args.ch, args.r, args.f, args.b, args.c, args.m, args.bc, args.reboot, args.app]):
        getAllSettings(session, ip, args.u, args.p)
    if args.country:
        setTime(session, ip, args.u, args.p, args.country)
    if args.reboot:
        print("reboot")
        reboot_dvr(session, ip, args.u, args.p)
    print("fin")

# Main function
def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, required=True)
    parser.add_argument("--u", type=str, required=True)
    parser.add_argument("--p", type=str, required=True)
    parser.add_argument("--ch", type=str, required=False)
    parser.add_argument("--r", type=str, required=False)
    parser.add_argument("--f", type=int, required=False)
    parser.add_argument("--b", type=int, required=False)
    parser.add_argument("--c", type=str, required=False)
    parser.add_argument("--m", type=str, required=False)
    parser.add_argument("--bc", type=str, required=False)
    parser.add_argument("--country", type=str, required=False)
    parser.add_argument("--app", action="store_true", required=False)
    parser.add_argument("--reboot", action="store_true", required=False)

    args = parser.parse_args(args)
    session = requests.Session()

    if "{" in args.ip and not args.app:
        print("update")
        print("camera ip")
        ip_list = expand_ip_range(args.ip)
        print(ip_list)
        for ip in ip_list:
            print("***")
            print("Camera : " + str(ip.split(".")[3]))
            execute_actions(session, ip, args, "yes")
    elif "{" not in args.ip and args.app:
        print("display")
        execute_actions(session, args.ip, args, "no")
        print("possibility to display : ")
        getAllSettings(session, args.ip, args.u, args.p)
    elif "{" in args.ip and args.app:
        print("display")
        print("camera ip")
        ip_list = expand_ip_range(args.ip)
        print(ip_list)
        for ip in ip_list:
            print("***")
            print("Camera : " + str(ip.split(".")[3]))
            execute_actions(session, ip, args, "yes")
        print("possibility to display : ")
        getAllSettings(session, ip_list[0], args.u, args.p)
    else:
        print("update")
        execute_actions(session, args.ip, args, "no")

if __name__ == "__main__":
    main()