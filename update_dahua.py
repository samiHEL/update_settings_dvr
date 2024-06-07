import requests
from requests.auth import HTTPDigestAuth
import re
import argparse
import subprocess
from datetime import datetime
import pytz

# Créer une liste d'adresses IP pour les caméras IP
def expand_ip_range(ip_range):
    ip_list = []
    match = re.match(r'^(\d+\.\d+\.\d+\.)\{([\d,]+)\}$', ip_range)
    if match:
        prefix = match.group(1)
        numbers = match.group(2).split(',')
        for num in numbers:
            ip_list.append(prefix + num)
    return ip_list

# Trouver les ports ouverts sur un DVR ou une caméra IP
def scan_ports(target_ip):
    open_ports = []
    command = ['nmap', target_ip, '-p', '1-65535', '--open']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode == 0:
        lines = output.decode('utf-8').split('\n')
        for line in lines:
            if '/tcp' in line:
                port = int(line.split('/')[0])
                open_ports.append(port)
                print(f"Port {port} is open")
        return open_ports
    else:
        print(f"Erreur lors de l'exécution de la commande Nmap: {error.decode('utf-8')}")
        return None

# Vérifier si le port est un port HTTP
def is_http_port(camera_ip, username, password, port):
    url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode[1].ExtraFormat[0]"
    url2 = f'http://www.google.com:{port}'
    try:
        r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password), timeout=5)
        r.raise_for_status()
        print(f"test fonctionnel avec port {port}")
        return True
    except (requests.exceptions.RequestException):
        try:
            r = requests.get(url2, stream=True, auth=HTTPDigestAuth(username, password), timeout=5)
            r.raise_for_status()
            print(f"test fonctionnel avec port {port}")
            return True
        except:
            print(f"erreur avec port {port}")
            return False

# Afficher les résultats
def print_results(compression_types, resolution_types, fps_types, bitrate_types):
    print(f'Compression_types : {compression_types}')
    print(f'Resolution_types: {resolution_types}')
    print(f'Fps_types : {fps_types}')
    print(f'Bitrate_types: {bitrate_types.replace(",", "-")}')

def print_results_cam(compression_types, resolution_types, fps_types, bitrate_types, channel, bitratecontrol):
    print(f'channel : {channel}')
    print(f'Compression_types : {compression_types}')
    print(f'Resolution_types: {resolution_types}')
    print(f'Fps_types : {fps_types}')
    print(f'bitrate control : {bitratecontrol}')
    print(f'Bitrate_types: {bitrate_types.replace(",", "-")}')

# Trouver le nombre de caméras sur un DVR
def numberCam(camera_ip, username, password):
    open_ports = scan_ports(camera_ip)
    potential_http_ports = []
    for port in open_ports:
        if is_http_port(camera_ip, username, password, port):
            potential_http_ports.append(port)
            break
    if potential_http_ports:
        print(f"Le ports HTTP potentiel est: {potential_http_ports[0]}")
    else:
        print("Aucun port HTTP potentiel trouvé.")
    port = potential_http_ports[0]
    url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Ptz"
    r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password))
    t = r.text
    matches = re.findall(r'table\.Ptz\[(\d+)\]', t)
    if matches:
        dernier_chiffre = int(matches[-1])
        return [dernier_chiffre + 1, port]
    else:
        print("nombre de camera introuvable")
        return [1, port]

# Obtenir des informations sur la caméra
def getinfoCam(camera_ip, username, password, channel_id, cam):
    print(camera_ip)
    number = numberCam(camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1
    for x in range(nbCam):
        if channel_id == "all_sub":
            sub = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode[{x}].ExtraFormat[0]"
        else:
            sub = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode[{x}].MainFormat[0]"
        r = requests.get(sub, stream=True, auth=HTTPDigestAuth(username, password))
        print(r.status_code)
        if r.status_code == 401:
            print("Unauthorized")
        if r.status_code == 200:
            print("-----")
            try:
                target_line_compression = next(line for line in r.text.split('\n') if f'table.Encode[{x}].{"ExtraFormat[0]" if channel_id == "all_sub" else "MainFormat[0]"}.Video.Compression' in line)
                compression_types = target_line_compression.split('=')[1].strip()
                target_line_resolution = next(line for line in r.text.split('\n') if f'table.Encode[{x}].{"ExtraFormat[0]" if channel_id == "all_sub" else "MainFormat[0]"}.Video.resolution' in line)
                resolution_types = target_line_resolution.split('=')[1].strip()
                target_line_fps = next(line for line in r.text.split('\n') if f'table.Encode[{x}].{"ExtraFormat[0]" if channel_id == "all_sub" else "MainFormat[0]"}.Video.FPS' in line)
                fps_types = target_line_fps.split('=')[1].strip()
                target_line_bitrate = next(line for line in r.text.split('\n') if f'table.Encode[{x}].{"ExtraFormat[0]" if channel_id == "all_sub" else "MainFormat[0]"}.Video.BitRate' in line)
                bitrate_types = target_line_bitrate.split('=')[1].strip()
                bitrate_control = next(line for line in r.text.split('\n') if f'table.Encode[{x}].{"ExtraFormat[0]" if channel_id == "all_sub" else "MainFormat[0]"}.Video.BitRateControl' in line)
                bitrate_ctrl = bitrate_control.split('=')[1].strip()
                print_results_cam(compression_types, resolution_types, fps_types, bitrate_types, str(x + 1), bitrate_ctrl)
            except:
                continue

# Obtenir tous les paramètres
def getAllSettings(camera_ip, username, password):
    number = numberCam(camera_ip, username, password)
    port = number[1]
    url = f"http://{camera_ip}:{port}/cgi-bin/encode.cgi?action=getConfigCaps"
    url_user = f"http://{camera_ip}:{port}/cgi-bin/userManager.cgi?action=getUserInfoAll"
    r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password))
    r_user = requests.get(url_user, stream=True, auth=HTTPDigestAuth(username, password))
    print(r.status_code)
    if r.status_code == 401:
        print("Unauthorized")
    if r.status_code == 200:
        print(f"Pour IP {camera_ip}")
        print("INFO USER :")
        text_user = r_user.text
        name_pattern = re.compile(r"users\[(\d+)\]\.Name=(\w+)")
        group_pattern = re.compile(r"users\[(\d+)\]\.Group=(\w+)")
        authority_pattern = re.compile(r"users\[(\d+)\]\.AuthorityList\[\d+\]=(\w+)")
        names, groups, authorities = {}, {}, {}

        for match in name_pattern.finditer(text_user):
            user_index, name = match.groups()
            names[int(user_index)] = name

        for match in group_pattern.finditer(text_user):
            user_index, group = match.groups()
            groups[int(user_index)] = group

        for match in authority_pattern.finditer(text_user):
            user_index, authority = match.groups()
            authorities.setdefault(int(user_index), []).append(authority)

        for user_index in names.keys():
            print(f"User {user_index}")
            print(f"Name: {names[user_index]}")
            print(f"Group: {groups[user_index]}")
            print(f"Droit: {authorities[user_index]}")
            print()
        print("-----------")
        try:
            try:
                target_line_compression = next(line for line in r.text.split('\n') if 'caps[0].MainFormat[0].Video.CompressionTypes' in line)
                compression_types = target_line_compression.split('=')[1].strip()
                target_line_resolution = next(line for line in r.text.split('\n') if 'caps[0].MainFormat[0].Video.ResolutionTypes' in line)
                resolution_types = target_line_resolution.split('=')[1].strip()
                target_line_fps = next(line for line in r.text.split('\n') if 'caps[0].MainFormat[0].Video.FPSMax' in line)
                fps_types = target_line_fps.split('=')[1].strip()
                target_line_bitrate = next(line for line in r.text.split('\n') if 'caps[0].MainFormat[0].Video.BitRateOptions' in line)
                bitrate_types = target_line_bitrate.split('=')[1].strip()
                print("Flux primaire")
                print_results(compression_types, resolution_types, fps_types, bitrate_types)
                print("-----------")
                target_line_compression = next(line for line in r.text.split('\n') if 'caps[0].ExtraFormat[0].Video.CompressionTypes' in line)
                compression_types = target_line_compression.split('=')[1].strip()
                target_line_resolution = next(line for line in r.text.split('\n') if 'caps[0].ExtraFormat[0].Video.ResolutionTypes' in line)
                resolution_types = target_line_resolution.split('=')[1].strip()
                target_line_fps = next(line for line in r.text.split('\n') if 'caps[0].ExtraFormat[0].Video.FPSMax' in line)
                fps_types = target_line_fps.split('=')[1].strip()
                target_line_bitrate = next(line for line in r.text.split('\n') if 'caps[0].ExtraFormat[0].Video.BitRateOptions' in line)
                bitrate_types = target_line_bitrate.split('=')[1].strip()
                print("Flux secondaire")
                print_results(compression_types, resolution_types, fps_types, bitrate_types)
                print("-----------")
            except:
                target_line_compression = next(line for line in r.text.split('\n') if 'caps.MainFormat[0].Video.CompressionTypes' in line)
                compression_types = target_line_compression.split('=')[1].strip()
                target_line_resolution = next(line for line in r.text.split('\n') if 'caps.MainFormat[0].Video.ResolutionTypes' in line)
                resolution_types = target_line_resolution.split('=')[1].strip()
                target_line_fps = next(line for line in r.text.split('\n') if 'caps.MainFormat[0].Video.FPSMax' in line)
                fps_types = target_line_fps.split('=')[1].strip()
                target_line_bitrate = next(line for line in r.text.split('\n') if 'caps.MainFormat[0].Video.BitRateOptions' in line)
                bitrate_types = target_line_bitrate.split('=')[1].strip()
                print("Flux primaire")
                print_results(compression_types, resolution_types, fps_types, bitrate_types)
                print("-----------")
                target_line_compression = next(line for line in r.text.split('\n') if 'caps.ExtraFormat[0].Video.CompressionTypes' in line)
                compression_types = target_line_compression.split('=')[1].strip()
                target_line_resolution = next(line for line in r.text.split('\n') if 'caps.ExtraFormat[0].Video.ResolutionTypes' in line)
                resolution_types = target_line_resolution.split('=')[1].strip()
                target_line_fps = next(line for line in r.text.split('\n') if 'caps.ExtraFormat[0].Video.FPSMax' in line)
                fps_types = target_line_fps.split('=')[1].strip()
                target_line_bitrate = next(line for line in r.text.split('\n') if 'caps.ExtraFormat[0].Video.BitRateOptions' in line)
                bitrate_types = target_line_bitrate.split('=')[1].strip()
                print("Flux secondaire")
                print_results(compression_types, resolution_types, fps_types, bitrate_types)
                print("-----------")
        except:
            print("Erreur interne")

def setParameter(camera_ip, username, password, channel_id, param, value, cam):
    number = numberCam(camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1
    if "all" in channel_id:
        for x in range(nbCam):
            print(x + 1)
            url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&Encode[{x}].{param}={value}"
            r = requests.put(url, stream=True, auth=HTTPDigestAuth(username, password))
            print(f"Set {param} for camera {x+1}: {r.status_code}")
            if r.status_code == 401:
                print("Unauthorized")
            elif r.status_code == 400 and param.endswith("resolution"):
                url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&Encode[{x}].{param}=704x576"
                r = requests.put(url, stream=True, auth=HTTPDigestAuth(username, password))
                print(f"Resolution too high, set to 704x576 for camera {x+1}")
            elif r.status_code != 200:
                print(f"Erreur : {r.status_code} - {r.text}")
    else:
        channel_id = int(channel_id) - 1
        url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&Encode[{channel_id}].{param}={value}"
        r = requests.put(url, stream=True, auth=HTTPDigestAuth(username, password))
        print(f"Set {param} for camera {channel_id+1}: {r.status_code}")
        if r.status_code == 401:
            print("Unauthorized")
        elif r.status_code == 400 and param.endswith("resolution"):
            url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&Encode[{channel_id}].{param}=704x576"
            r = requests.put(url, stream=True, auth=HTTPDigestAuth(username, password))
            print(f"Resolution too high, set to 704x576 for camera {channel_id+1}")
        elif r.status_code != 200:
            print(f"Erreur : {r.status_code} - {r.text}")

def setDetection(camera_ip, username, password, channel_id, motionDetect, cam):
    channel_id = int(channel_id) - 1
    url_detection = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&MotionDetect[{channel_id}].Enable={motionDetect.lower()}"
    r = requests.put(url_detection, stream=True, auth=HTTPDigestAuth(username, password))
    print(f"Set motion detection for camera {channel_id+1}: {r.status_code}")
    if r.status_code == 401:
        print("Unauthorized")
    elif r.status_code == 200:
        number = numberCam(camera_ip, username, password)
        port = number[1]
        nbCam = int(number[0])
        if cam == "yes":
            nbCam = 1
        for x in range(nbCam):
            url_detection = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&MotionDetect[{x}].Enable={motionDetect.lower()}"
            r = requests.put(url_detection, stream=True, auth=HTTPDigestAuth(username, password))
            print(f"Set motion detection for camera {x+1}: {r.status_code}")
            if r.status_code == 401:
                print("Unauthorized")
            elif r.status_code == 400:
                print("Pas bon format !")
            else:
                print(f"Erreur : {r.status_code} - {r.text}")

def setEncrypt(camera_ip, username, password):
    urls = [
        f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.wlan0.Enable=true",
        f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.wlan0.KeyFlag=true",
        f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.wlan0.Encryption=On",
        f"http://{camera_ip}/cgi-bin/configManager.cgi?action=getConfig&name=WLan"
    ]
    for url in urls:
        r = requests.put(url, stream=True, auth=HTTPDigestAuth(username, password)) if "setConfig" in url else requests.get(url, stream=True, auth=HTTPDigestAuth(username, password))
        print(r.status_code)
        if r.status_code == 200:
            print(r.text)

def get_country_time(pays):
    try:
        country_timezone = pytz.country_timezones.get(pays.upper())
        if country_timezone:
            country_time = datetime.now(pytz.timezone(country_timezone[0]))
            return country_time.strftime("%Y-%m-%d%%20%H:%M:%S")
        else:
            return f"Impossible de trouver le fuseau horaire pour le pays avec le code {pays}."
    except Exception as e:
        print("Une erreur s'est produite lors de la récupération de l'heure du pays :", e)
        return None

def setTime(camera_ip, username, password, country):
    number = numberCam(camera_ip, username, password)
    port = number[1]
    auth = HTTPDigestAuth(username, password)
    url_before = f"http://{camera_ip}:{port}/cgi-bin/global.cgi?action=getCurrentTime"
    response_before = requests.get(url_before, auth=auth, timeout=5)
    print('Time before change :')
    print(response_before.text)
    local_now_string = get_country_time(country)
    url_time = f"http://{camera_ip}:{port}/cgi-bin/global.cgi?action=setCurrentTime&time=" + local_now_string
    response_time = requests.post(url_time, auth=auth, timeout=5)
    if response_time.status_code == 200:
        print('Time change successful!')
    response_before = requests.get(url_before, auth=auth, timeout=5)
    print('New Time :')
    print(response_before.text)

def reboot_dvr(camera_ip, username, password):
    number = numberCam(camera_ip, username, password)
    port = number[1]
    auth = HTTPDigestAuth(username, password)
    url_reboot = f"http://{camera_ip}:{port}/cgi-bin/magicBox.cgi?action=reboot"
    response_reboot = requests.get(url_reboot, auth=auth, timeout=5)
    if response_reboot.status_code == 200:
        print('The device was successfully restarted.')

if __name__ == "__main__":
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
    parser.add_argument("--reboot", type=str, required=False)
    args = parser.parse_args()

    ip_list = expand_ip_range(args.ip) if "{" in args.ip else [args.ip]
    for ip in ip_list:
        if args.r:
            setParameter(ip, args.u, args.p, args.ch, "ExtraFormat[0].Video.resolution", args.r, "yes")
        if args.f:
            setParameter(ip, args.u, args.p, args.ch, "ExtraFormat[0].Video.FPS", args.f, "yes")
        if args.b:
            setParameter(ip, args.u, args.p, args.ch, "ExtraFormat[0].Video.BitRate", args.b, "yes")
        if args.c:
            setParameter(ip, args.u, args.p, args.ch, "ExtraFormat[0].Video.Compression", args.c, "yes")
        if args.m:
            setDetection(ip, args.u, args.p, args.ch, args.m, "yes")
        if args.bc:
            setParameter(ip, args.u, args.p, args.ch, "ExtraFormat[0].Video.BitRateControl", args.bc, "yes")
        if args.ch and not any([args.r, args.f, args.b, args.c, args.m]):
            getinfoCam(ip, args.u, args.p, args.ch, "yes")
        if not any([args.ch, args.r, args.f, args.b, args.c, args.m, args.bc, args.reboot]):
            getAllSettings(ip, args.u, args.p)
        if args.country:
            setTime(ip, args.u, args.p, args.country)
        if args.reboot:
            reboot_dvr(ip, args.u, args.p)
