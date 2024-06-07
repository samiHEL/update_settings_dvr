import requests
from requests.auth import HTTPDigestAuth
import re
import argparse
import xml.etree.ElementTree as ET

ns = {'ns': 'http://www.hikvision.com/ver20/XMLSchema'}
ns2 = {'xmlns': 'http://www.hikvision.com/ver20/XMLSchema'}
ns3 = {'xmlns': 'http://www.std-cgi.com/ver20/XMLSchema'}
ns4 = {'xmlns': 'http://www.std-cgi.org/ver20/XMLSchema'}
ns5 = {'xmlns': 'http://www.isapi.com/ver20/XMLSchema'}
ns6 = {'xmlns': 'http://www.isapi.org/ver20/XMLSchema'}



from datetime import datetime
import pytz
import subprocess
import time
import importlib



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

    # Exécute la commande Nmap avec les options spécifiées
    command = ['nmap', target_ip, '-p', '1-65535', '--open']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    # Vérifie si l'exécution de la commande a réussi
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



def is_http_port(camera_ip, username, password, port):
    url = f'http://www.google.com:{port}' 
    url2 = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/101'
    
    try:
        r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password), timeout=5)
        r.raise_for_status()
        print("test fonctionnel avec port  "+str(port))
        return True  # La connexion a réussi, donc c'est potentiellement un port HTTP
    except (requests.exceptions.RequestException):
        try:
            r = requests.get(url2, stream=True, auth=HTTPDigestAuth(username, password), timeout=5)
            r.raise_for_status()
            print("test fonctionnel avec port  "+str(port))
            return True
        except:   
            print("erreur avec port "+str(port))
            return False  # La connexion a échoué
        
   
def set_resolution(camera_ip, username, password, channel_id, resolution, cam):
    resolution_width, resolution_height = resolution.split("x")
    number = get_param(camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1

    def modify_resolution(camera_index, stream_type):
        channel = camera_index + 1
        channel2 = f"{channel:02d}{stream_type}"
        url_image_settings = f"http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}"
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
        
        if response_get.status_code == 200:
            xml = response_get.text
            xml = re.sub(r"<videoResolutionWidth>.*?</videoResolutionWidth>", f"<videoResolutionWidth>{resolution_width}</videoResolutionWidth>", xml)
            xml = re.sub(r"<videoResolutionHeight>.*?</videoResolutionHeight>", f"<videoResolutionHeight>{resolution_height}</videoResolutionHeight>", xml)
            response_put = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
            
            if response_put.status_code == 200:
                print(f"Resolution pour camera {channel2} mise à {resolution}")
            else:
                print(f"Erreur : {response_put.status_code} - {response_put.text}")
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")

    if "all" in channel_id:
        for x in range(nbCam):
            print(x + 1)
            if "main" in channel_id:
                modify_resolution(x, "01")
            elif "sub" in channel_id:
                modify_resolution(x, "02")
    else:
        channel_index = int(channel_id) - 1
        modify_resolution(channel_index, "02")

def set_fps(camera_ip, username, password, channel_id, fps, cam):
    number = get_param(camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1

    def modify_fps(camera_index, stream_type):
        channel = camera_index + 1
        channel2 = f"{channel:02d}{stream_type}"
        url_image_settings = f"http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}"
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
        
        if response_get.status_code == 200:
            xml = response_get.text
            xml = re.sub(r"<maxFrameRate>.*?</maxFrameRate>", f"<maxFrameRate>{fps * 100}</maxFrameRate>", xml)
            response_put = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
            
            if response_put.status_code == 200:
                print(f"Fps pour camera {channel2} mise à {fps}")
            else:
                print(f"Erreur : {response_put.status_code} - {response_put.text}")
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")

    if "all" in channel_id.lower():
        for x in range(nbCam):
            print(x + 1)
            if "main" in channel_id.lower():
                modify_fps(x, "01")
            elif "sub" in channel_id.lower():
                modify_fps(x, "02")
    else:
        modify_fps(int(channel_id) - 1, "02")


def set_bitrate(camera_ip, username, password, channel_id, BitRate, cam):
    number = get_param(camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1

    def modify_bitrate(camera_index, stream_type):
        channel = camera_index + 1
        channel2 = f"{channel:02d}{stream_type}"
        url_image_settings = f"http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}"
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
        
        if response_get.status_code == 200:
            xml = response_get.text
            try:
                xml = re.sub(r"<vbrUpperCap>.*?</vbrUpperCap>", f"<vbrUpperCap>{BitRate}</vbrUpperCap>", xml)
            except:
                xml = re.sub(r"<constantBitRate>.*?</constantBitRate>", f"<constantBitRate>{BitRate}</constantBitRate>", xml)
            response_put = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
            
            if response_put.status_code == 200:
                print(f"Bitrate pour camera {channel2} mise à {BitRate}")
            else:
                print(f"Erreur : {response_put.status_code} - {response_put.text}")
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")

    if "all" in channel_id.lower():
        for x in range(nbCam):
            print(x + 1)
            if "main" in channel_id.lower():
                modify_bitrate(x, "01")
            elif "sub" in channel_id.lower():
                modify_bitrate(x, "02")
    else:
        modify_bitrate(int(channel_id) - 1, "02")



def set_bitrateControl(camera_ip, username, password, channel_id, bcr, cam):
    number = get_param(camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1

    def modify_bitrateControl(camera_index, stream_type):
        channel = camera_index + 1
        channel2 = f"{channel:02d}{stream_type}"
        url_image_settings = f"http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}"
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
        
        if response_get.status_code == 200:
            xml = response_get.text
            xml = re.sub(r"<videoQualityControlType>.*?</videoQualityControlType>", f"<videoQualityControlType>{bcr}</videoQualityControlType>", xml)
            response_put = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
            
            if response_put.status_code == 200:
                print(f"Bitrate Control pour camera {channel2} mis à {bcr}")
            else:
                print(f"Erreur : {response_put.status_code} - {response_put.text}")
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")

    if "all" in channel_id.lower():
        for x in range(nbCam):
            print(x + 1)
            if "main" in channel_id.lower():
                modify_bitrateControl(x, "01")
            elif "sub" in channel_id.lower():
                modify_bitrateControl(x, "02")
    else:
        modify_bitrateControl(int(channel_id) - 1, "02")


def set_compression(camera_ip, username, password, channel_id, compression,cam):
    number=get_param(camera_ip, username, password)
    port=number[1]
    nbCam=int(number[0])
    if cam == "yes":
        nbCam = 1
    if "all"in channel_id:
        for x in range(nbCam):
            print(x+1)
            if channel_id=="all_main":
                channel=x+1
                channel2=str(channel)+"01"
            elif channel_id=="all_sub":
                channel=x+1
                channel2=str(channel)+"02"
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}'
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")
            xml = re.sub(r"<videoCodecType>.*?</videoCodecType>", f"<videoCodecType>{compression}</videoCodecType>", xml)
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
            if response.status_code == 200:
                print("Compression pour camera "+str(channel2)+" mise à "+compression) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")
    else:
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel_id}'
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")
            xml = re.sub(r"<videoCodecType>.*?</videoCodecType>", f"<videoCodecType>{compression}</videoCodecType>", xml)
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
            if response.status_code == 200:
                print("Compression pour camera "+str(channel_id)+" mise à "+compression) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")



def get_camera_parameters(camera_ip, username, password, channel_id, cam):
    number = get_param(camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1

    def fetch_and_parse(channel2):
        url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}/'
        try:
            response = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
            if response.status_code == 200:
                xml = response.text
                root = ET.fromstring(xml)
                namespace_uri = root.tag.split('}', 1)[0][1:]

                if namespace_uri in ns['ns']:
                    data = parse_xml(root, ns)
                elif namespace_uri in ns2['xmlns']:
                    data = parse_xml(root, ns2)
                elif namespace_uri in ns3['xmlns']:
                    data = parse_xml(root, ns3)
                elif namespace_uri in ns4['xmlns']:
                    data = parse_xml(root, ns4)
                elif namespace_uri in ns6['xmlns']:
                    data = parse_xml(root, ns6)
                else:
                    data = {}

                if data:
                    print_results(**data)
                    print("-----------")
                else:
                    print(f"Erreur : {response.status_code} - {response.text}")

            else:
                print(f"Erreur : {response.status_code} - {response.text}")

        except requests.RequestException as e:
            print(f"Erreur de requête : {e}")

    def parse_xml(root, ns):
        try:
            id_channel = root.find('.//ns:channelName', namespaces=ns).text
            width_resolution = root.find('.//ns:videoResolutionWidth', namespaces=ns).text
            height_resolution = root.find('.//ns:videoResolutionHeight', namespaces=ns).text
            image_par_sec = root.find('.//ns:maxFrameRate', namespaces=ns).text

            constant_bit_rate = root.find('.//ns:constantBitRate', namespaces=ns).text if root.find('.//ns:constantBitRate', namespaces=ns) else None
            vbr_Upper_Cap = root.find('.//ns:vbrUpperCap', namespaces=ns).text if root.find('.//ns:vbrUpperCap', namespaces=ns) else None

            type_bande_passante = 'Constant' if constant_bit_rate else 'Variable'
            debit_bin_max = constant_bit_rate if constant_bit_rate else vbr_Upper_Cap
            encodage_video = root.find('.//ns:videoCodecType', namespaces=ns).text

            return {
                'id_channel': id_channel,
                'width_resolution': width_resolution,
                'height_resolution': height_resolution,
                'type_bande_passante': type_bande_passante,
                'image_par_sec': image_par_sec,
                'debit_bin_max': debit_bin_max,
                'encodage_video': encodage_video
            }
        except Exception as e:
            print(f"Erreur lors de l'analyse XML : {e}")
            return {}

    if "all" in channel_id.lower():
        for x in range(nbCam):
            print(x + 1)
            channel = x + 1
            if "main" in channel_id.lower():
                fetch_and_parse(f"{channel:02d}01")
            elif "sub" in channel_id.lower():
                fetch_and_parse(f"{channel:02d}02")
    else:
        fetch_and_parse(channel_id)



def encryption(camera_ip, username, password, param):
    number=get_param(camera_ip, username, password)
    port=number[1]
    #url = f'http://{camera_ip}:{port}/ISAPI/System/Network/capabilities'EZVIZ
    url = f'http://{camera_ip}:{port}/ISAPI/System/Network/EZVIZ'
    #url = f'http://{camera_ip}:{port}/ISAPI/System/capabilities'
    #url = f'http://{camera_ip}:{port}/ISAPI/Streaming/encryption/capabilities?format=json'
    #url = f'http://{camera_ip}:{port}/ISAPI/Streaming/encryption/secretKey?format=json'
    
    #reponse -> <isSupportStreamingEncrypt>true</isSupportStreamingEncrypt>
    response = requests.get(url, auth=HTTPDigestAuth(username, password))

    if response.status_code == 200:
        xml = response.text
        print("--------------- PARAMETRE AVANT CHANGEMENT ---------------" )
        print(xml)
        print("------------------------------")
    else:
        print(f"Erreur : {response.status_code} - {response.text}")
        return
    if param.lower() =="true":
        xml = re.sub(r"<enabled>.*?</enabled>", f"<enabled>true</enabled>", xml)
    else:
        xml = re.sub(r"<enabled>.*?</enabled>", f"<enabled>false</enabled>", xml)

    response = requests.put(url, auth=HTTPDigestAuth(username, password), data=xml)
    if response.status_code == 200:
        print(response.status_code)
        print("--------------- PARAMETRE APRES CHANGEMENT ---------------")
        print(xml)
        print("------------------------------")
    else:
        print(f"Erreur : {response.status_code} - {response.text}")

def get_camera_parameters_unique(camera_ip, username, password):
    number = get_param(camera_ip, username, password)
    port = number[1]
    url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Security/users/'
    
    print("Pour IP " + camera_ip)
    response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
    if response_get.status_code == 200:
        print(response_get.text)
    else:
        print(f"Erreur : {response_get.status_code} - {response_get.text}")

    urls = [
        (f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/101/capabilities', "primaire"),
        (f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/102/capabilities', "secondaire")
    ]

    for url, flux_type in urls:
        fetch_and_print(url, flux_type, username, password)

def fetch_and_print(url, flux_type, username, password):
    try:
        response = requests.get(url, auth=HTTPDigestAuth(username, password))
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            namespace_uri = root.tag.split('}', 1)[0][1:]

            data = parse_capabilities(root, namespace_uri)
            if data:
                print(f"// Flux {flux_type} //")
                print_settings(data['videoCodec_opt'], data['videoResolutionWidth_opt'], data['videoResolutionHeight_opt'], data['maxFrameRate_opt_list'], data['constantBitRate_opt'])
                print("---------------------")
            else:
                print(f"Erreur : {response.status_code} - {response.text}")

        else:
            print(f"Erreur : {response.status_code} - {response.text}")

    except requests.RequestException as e:
        print(f"Erreur de requête : {e}")

def parse_capabilities(root, namespace_uri):
    try:
        ns = get_namespace(namespace_uri)
        videoCodecTypeElement = root.find(f'.//{ns}:videoCodecType', namespaces={ns: namespace_uri})
        videoCodec_opt = videoCodecTypeElement.attrib['opt']

        videoResolutionWidth = root.find(f'.//{ns}:videoResolutionWidth', namespaces={ns: namespace_uri})
        videoResolutionWidth_opt = videoResolutionWidth.attrib['opt']

        videoResolutionHeight = root.find(f'.//{ns}:videoResolutionHeight', namespaces={ns: namespace_uri})
        videoResolutionHeight_opt = videoResolutionHeight.attrib['opt']

        maxFrameRate = root.find(f'.//{ns}:maxFrameRate', namespaces={ns: namespace_uri})
        maxFrameRate_opt = maxFrameRate.attrib['opt']
        maxFrameRate_opt_list = [int(x) / 100 for x in maxFrameRate_opt.split(',') if x]

        constantBitRate = root.find(f'.//{ns}:constantBitRate', namespaces={ns: namespace_uri})
        constantBitRate_min = constantBitRate.attrib['min']
        constantBitRate_max = constantBitRate.attrib['max']
        constantBitRate_opt = {"valeur min": constantBitRate_min, "valeur max": constantBitRate_max}

        return {
            'videoCodec_opt': videoCodec_opt,
            'videoResolutionWidth_opt': videoResolutionWidth_opt,
            'videoResolutionHeight_opt': videoResolutionHeight_opt,
            'maxFrameRate_opt_list': maxFrameRate_opt_list,
            'constantBitRate_opt': constantBitRate_opt
        }
    except Exception as e:
        print(f"Erreur lors de l'analyse XML : {e}")
        return {}

def get_namespace(uri):
    if uri == ns['ns']:
        return 'ns'
    elif uri == ns2['xmlns']:
        return 'xmlns'
    elif uri == ns3['xmlns']:
        return 'xmlns'
    elif uri == ns4['xmlns']:
        return 'xmlns'
    elif uri == ns5['xmlns']:
        return 'xmlns'
    elif uri == ns6['xmlns']:
        return 'xmlns'
    else:
        return None
    
def get_param(camera_ip, username, password):
    open_ports=scan_ports(camera_ip)
    print(open_ports)
    potential_http_ports = []
    for port in open_ports:
        try:
            if is_http_port(camera_ip, username, password, port):
                potential_http_ports.append(port)
                break 
        except:
            print(f"L'itération pour le port {port} a pris trop de temps (plus de 30 secondes).")
    if potential_http_ports:
        print(f"Le ports HTTP potentiel est: {potential_http_ports[0]}")
    else:
        print("Aucun port HTTP potentiel trouvé.")
    url_image_settings = f'http://{camera_ip}:{port}/ISAPI/System/Video/inputs/channels/'
    response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
    if response_get.status_code == 200:
        xml = response_get.text
        namespace = {'ns': 'http://www.hikvision.com/ver20/XMLSchema'}
        root = ET.fromstring(xml)
        match = re.search(r"<inputPort>(\d+)</inputPort>(?:(?!<inputPort>).)*$", xml, re.DOTALL)
        
        if match:
            valeur_input_port = match.group(1)
            return [valeur_input_port,port]
        else:
            print("Balise inputPort non trouvée dans le dernier VideoInputChannel.")
    else:
        print(f"Erreur : {response_get.status_code} - {response_get.text}")
        return [30,port]

def set_motion(camera_ip, username, password, channel_id, motionDetect,cam):
    number=get_param(camera_ip, username, password)
    port=number[1]
    nbCam=int(number[0])
    if cam == "yes":
        nbCam = 1
    if "all" in channel_id:
        for x in range(nbCam):
            print(x+1)
            if channel_id=="all_main":
                channel2=x+1
            elif channel_id=="all_sub":
                channel2=x+1
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/System/Video/inputs/channels/{channel2}/MotionDetection'
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
            if response_get.status_code == 200:
                xml = response_get.text
                print(xml)
                print("------------------------------")
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")
            xml = re.sub(r"<enabled>.*?</enabled>", f"<enabled>{motionDetect.lower()}</enabled>", xml)
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
            if response.status_code == 200:
                print("Detection mouvement pour camera "+str(channel_id)+" mise à "+motionDetect.lower()) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")

                set_motion(camera_ip, username, password, channel_id, motionDetect)
    else:
        url_image_settings = f'http://{camera_ip}:{port}/ISAPI/System/Video/inputs/channels/{channel_id}/MotionDetection'
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
        if response_get.status_code == 200:
            xml = response_get.text
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")
        xml = re.sub(r"<enabled>.*?</enabled>", f"<enabled>{motionDetect.lower()}</enabled>", xml)
        response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
        if response.status_code == 200:
            print("Detection mouvement pour camera "+str(channel_id)+" mise à "+motionDetect.lower()) 
        else:
            print(f"Erreur : {response.status_code} - {response.text}")

def get_country_time(pays):
    try:
        # Obtenez le fuseau horaire du pays à partir du code de pays
        country_timezone = pytz.country_timezones.get(pays.upper())
        if country_timezone:
            # Convertir l'heure UTC actuelle au fuseau horaire du pays
            country_time = datetime.now(pytz.timezone(country_timezone[0]))
            country_time_formatted = country_time.strftime("%Y-%m-%dT%H:%M:%S")
            return country_time_formatted

        else:
            return f"Impossible de trouver le fuseau horaire pour le pays avec le code {'GB'}."
    except Exception as e:
        print("Une erreur s'est produite lors de la récupération de l'heure du pays :", e)
        return None

def setTime(camera_ip, username, password, country):
        number=get_param(camera_ip, username, password)
        port=number[1]
        url_image_settings = f'http://{camera_ip}:{port}/ISAPI/System/time'
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
        if response_get.status_code == 200:
            xml = response_get.text
            root = ET.fromstring(xml)
            local_time_element = root.find('.//{http://www.std-cgi.com/ver20/XMLSchema}localTime')
            local_time_content = local_time_element.text
            print('Time before change :')
            print(local_time_content)
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")
        time = get_country_time(country)
        xml = re.sub(r"<localTime>.*?</localTime>", f"<localTime>{time}</localTime>", xml)
        response_put = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
        if response_put.status_code == 200:
            print('Time change successful!')
        else:
            print(f"Erreur : {response_put.status_code} - {response_put.text}")

        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
        if response_get.status_code == 200:
            xml1 = response_get.text
            root1 = ET.fromstring(xml1)
                        # Find the <localTime> element and retrieve its text content
            local_time_element1 = root1.find('.//{http://www.std-cgi.com/ver20/XMLSchema}localTime')
            local_time_content1 = local_time_element1.text
            print('New time :')
            print(local_time_content1)
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")

def reboot_dvr(camera_ip, username, password):
    number=get_param(camera_ip, username, password)
    port=number[1]
    url_reboot = f'http://{camera_ip}:{port}/ISAPI/System/reboot'
    response = requests.put(url_reboot, auth=HTTPDigestAuth(username, password))
    if response.status_code == 200:
        print('The device was successfully restarted.')

def print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video):
    print('ID Channel :', id_channel)
    print('Resolution : ', str(width_resolution)+"x"+str(height_resolution))
    print('Type bande passante : ', type_bande_passante)
    if int(image_par_sec)==0:
        print('Image par seconde : MAX')
    else:
        print('Image par seconde : ', int(image_par_sec)/100 ,' fps')
    print('Debit binaire max : ', debit_bin_max)
    print('Encodage_video : ', encodage_video)

def print_settings(videoCodec_opt,videoResolutionWidth_opt,videoResolutionHeight_opt,maxFrameRate_opt_list,constantBitRate_opt):
    print('Video Codec :', videoCodec_opt)
    print('Video Resolution :', str(videoResolutionWidth_opt)+"//"+str(videoResolutionHeight_opt))
    print('FPS :', maxFrameRate_opt_list)
    print('Bitrate :', constantBitRate_opt)


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
    parser.add_argument("--encrypt", type=str, required=False)
    parser.add_argument("--country", type=str, required=False)
    parser.add_argument("--app", type=str, required=False)
    parser.add_argument("--reboot", type=str, required=False)


    args = parser.parse_args()
    if args.app=="yes":
        if "{" in args.ip :
            ip_list = expand_ip_range(args.ip)
            print(ip_list)
            for ip in ip_list:
                    get_camera_parameters(ip, args.u, args.p, args.ch,"yes")
                    print("debut")
                    if args.r!=None:
                        set_resolution(ip, args.u, args.p, args.ch, args.r,"yes")
                    if args.f!=None:
                        set_fps(ip, args.u, args.p, args.ch, args.f,"yes")
                    if args.b!=None:
                        set_bitrate(ip, args.u, args.p, args.ch, args.b,"yes")
                    if args.c!=None:
                        set_compression(ip, args.u, args.p, args.ch, args.c,"yes")
                    if args.m!=None:
                        set_motion(ip, args.u, args.p, args.ch, args.m,"yes")
                    if args.ch!=None and args.ch!="all" and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None:
                        get_camera_parameters(ip, args.u, args.p, args.ch,"yes")
                    if args.ch=="all" and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None and args.reboot == None:
                        get_camera_parameters(ip, args.u, args.p, "all_main","yes")
                        get_camera_parameters(ip, args.u, args.p, "all_sub","yes")
                    if args.ch==None and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None and args.reboot == None:
                        get_camera_parameters_unique(ip, args.u, args.p)
                    if args.country!=None:
                        setTime(ip, args.u, args.p, args.country)
                    if args.bc!=None:
                        set_bitrateControl(ip, args.u, args.p, args.ch, args.bc, "yes")
                    if args.u!=None and args.p!=None and ip!=None and args.reboot:
                        reboot_dvr(ip, args.u, args.p)
                    print("fin")
                    get_camera_parameters(ip, args.u, args.p, args.ch,"yes")

                    
        else:
            get_camera_parameters(args.ip, args.u, args.p, args.ch,"no")
            print("debut")
            if args.r!=None:
                set_resolution(args.ip, args.u, args.p, args.ch, args.r,"no")
            if args.f!=None:
                set_fps(args.ip, args.u, args.p, args.ch, args.f,"no")
            if args.b!=None:
                set_bitrate(args.ip, args.u, args.p, args.ch, args.b,"no")
            if args.c!=None:
                set_compression(args.ip, args.u, args.p, args.ch, args.c,"no")
            if args.m!=None:
                set_motion(args.ip, args.u, args.p, args.ch, args.m,"no")
            if args.encrypt!=None:
                encryption(args.ip, args.u, args.p, args.encrypt)
            if args.ch!=None and args.ch!="all" and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None:
                get_camera_parameters(args.ip, args.u, args.p, args.ch,"no")
            if args.ch=="all" and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None and args.reboot == None:
                get_camera_parameters(args.ip, args.u, args.p, "all_main","no")
                get_camera_parameters(args.ip, args.u, args.p, "all_sub","no")
            if args.ch==None and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None and args.reboot == None:
                get_camera_parameters_unique(args.ip, args.u, args.p)
            if args.country!=None:
                encryption(args.ip, args.u, args.p, args.country)
            if args.bc!=None:
                set_bitrateControl(args.ip, args.u, args.p, args.ch, args.bc, "no")
            if args.u!=None and args.p!=None and args.ip!=None and args.reboot:
                reboot_dvr(args.ip, args.u, args.p)
            print("fin")
            get_camera_parameters(args.ip, args.u, args.p, args.ch,"no")
    else:
        if "{" in args.ip :
            ip_list = expand_ip_range(args.ip)
            print(ip_list)
            for ip in ip_list:
                    if args.r!=None:
                        set_resolution(ip, args.u, args.p, args.ch, args.r,"yes")
                    if args.f!=None:
                        set_fps(ip, args.u, args.p, args.ch, args.f,"yes")
                    if args.b!=None:
                        set_bitrate(ip, args.u, args.p, args.ch, args.b,"yes")
                    if args.c!=None:
                        set_compression(ip, args.u, args.p, args.ch, args.c,"yes")
                    if args.m!=None:
                        set_motion(ip, args.u, args.p, args.ch, args.m,"yes")
                    if args.ch!=None and args.ch!="all" and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None:
                        get_camera_parameters(ip, args.u, args.p, args.ch,"yes")
                    if args.ch=="all" and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None and args.reboot == None:
                        get_camera_parameters(ip, args.u, args.p, "all_main","yes")
                        get_camera_parameters(ip, args.u, args.p, "all_sub","yes")
                    if args.ch==None and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None and args.reboot == None:
                        get_camera_parameters_unique(ip, args.u, args.p)
                    if args.country!=None:
                        setTime(ip, args.u, args.p, args.country)
                    if args.bc!=None:
                        set_bitrateControl(ip, args.u, args.p, args.ch, args.bc, "yes")
                    if args.u!=None and args.p!=None and ip!=None and args.reboot:
                        reboot_dvr(ip, args.u, args.p)
        else:
            if args.r!=None:
                set_resolution(args.ip, args.u, args.p, args.ch, args.r,"no")
            if args.f!=None:
                set_fps(args.ip, args.u, args.p, args.ch, args.f,"no")
            if args.b!=None:
                set_bitrate(args.ip, args.u, args.p, args.ch, args.b,"no")
            if args.c!=None:
                set_compression(args.ip, args.u, args.p, args.ch, args.c,"no")
            if args.m!=None:
                set_motion(args.ip, args.u, args.p, args.ch, args.m,"no")
            if args.encrypt!=None:
                encryption(args.ip, args.u, args.p, args.encrypt)
            if args.ch!=None and args.ch!="all" and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None:
                get_camera_parameters(args.ip, args.u, args.p, args.ch,"no")
            if args.ch=="all" and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None and args.reboot == None:
                get_camera_parameters(args.ip, args.u, args.p, "all_main","no")
                get_camera_parameters(args.ip, args.u, args.p, "all_sub","no")
            if args.ch==None and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None and args.reboot == None:
                get_camera_parameters_unique(args.ip, args.u, args.p)
            if args.country!=None:
                encryption(args.ip, args.u, args.p, args.country)
            if args.bc!=None:
                set_bitrateControl(args.ip, args.u, args.p, args.ch, args.bc, "no")
            if args.u!=None and args.p!=None and args.ip!=None and args.reboot:
                reboot_dvr(args.ip, args.u, args.p)


## exemple commande Liste parametres flux primaire ou secondaire##
#python3 update_settings_dvr.py --camera_ip 172.24.1.105 --username admin --password Hikvision --channel_id 102

## exemple commande PUT parametres flux primaire ou secondaire##
##python3 update_settings_dvr.py --camera_ip 172.24.1.105 --username admin --password Hikvision --channel_id 102 --resolution 960x576

