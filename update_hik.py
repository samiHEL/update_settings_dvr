import argparse
import re
import xml.etree.ElementTree as ET

import requests
from requests.auth import HTTPDigestAuth

ns = {'ns': 'http://www.hikvision.com/ver20/XMLSchema'}
ns2 = {'xmlns': 'http://www.hikvision.com/ver20/XMLSchema'}
ns3 = {'xmlns': 'http://www.std-cgi.com/ver20/XMLSchema'}
ns4 = {'xmlns': 'http://www.std-cgi.org/ver20/XMLSchema'}
ns5 = {'xmlns': 'http://www.isapi.com/ver20/XMLSchema'}
ns6 = {'xmlns': 'http://www.isapi.org/ver20/XMLSchema'}
ns7 = {'xmlns': 'http://www.isapi.org/ver20/XMLSchema'}



import subprocess
from datetime import datetime

import pytz


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
    url2 = f'http://{camera_ip}:{port}/ISAPI/Security/users/'
    
    try:
            r = requests.get(url2, stream=True, auth=HTTPDigestAuth(username, password), timeout=3)
            r.raise_for_status()
            print("test fonctionnel avec port  "+str(port))
            return True
    except (requests.exceptions.RequestException):
        try:
            r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password), timeout=3)
            r.raise_for_status()
            print("test fonctionnel avec port  "+str(port))
            return True  # La connexion a réussi, donc c'est potentiellement un port HTTP

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
        url_motion_get = f'http://{camera_ip}:{port}/ISAPI/System/Video/inputs/channels/{channel2[:-2]}/motionDetection'
        url_encrypt = f'http://{camera_ip}:{port}/ISAPI/System/Network/EZVIZ'
        
        try:
            response = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
            response_motion = requests.get(url_motion_get, auth=HTTPDigestAuth(username, password))
            response_encrypt = requests.get(url_encrypt, auth=HTTPDigestAuth(username, password))
            if response.status_code == 200 :
                xml = response.text
                xml2 = response_motion.text
                xml3 = response_encrypt.text
                root = ET.fromstring(xml)
                root2 = ET.fromstring(xml2)
                root3 = ET.fromstring(xml3)
                root.append(root2)
                root.append(root3)
                namespace_uri = root.tag.split('}', 1)[0][1:]
                namespace_uri2 = root2.tag.split('}', 1)[0][1:]
                namespace_uri3 = root3.tag.split('}', 1)[0][1:]

                data = parse_xml(root, namespace_uri, namespace_uri2, namespace_uri3)
                if data:
                    print_results(**data)
                    print("-----------")
                else:
                    print(f"Erreur : {response.status_code} - {response.text}")

            else:
                print(f"Erreur : {response.status_code} - {response.text}")

        except requests.RequestException as e:
            print(f"Erreur de requête : {e}")

    def parse_xml(root, namespace_uri, namespace_uri2, namespace_uri3):
        try:
            ns_map = {
                'ns0': namespace_uri,
                'ns1': namespace_uri2,
                'ns2': namespace_uri3,
            }

            id_channel = root.find('.//ns0:id', namespaces=ns_map).text
            width_resolution = root.find('.//ns0:videoResolutionWidth', namespaces=ns_map).text
            height_resolution = root.find('.//ns0:videoResolutionHeight', namespaces=ns_map).text
            image_par_sec = root.find('.//ns0:maxFrameRate', namespaces=ns_map).text
            try:
                constant_bit_rate = root.find('.//ns0:constantBitRate', namespaces=ns_map).text
            except:
                constant_bit_rate = root.find('.//ns0:vbrUpperCap', namespaces=ns_map).text
            vbr_Upper_Cap = root.find('.//ns0:vbrUpperCap', namespaces=ns_map).text if root.find('.//ns0:vbrUpperCap', namespaces=ns_map) else None

            type_bande_passante = 'Constant' if constant_bit_rate else 'Variable'
            debit_bin_max = constant_bit_rate if constant_bit_rate else vbr_Upper_Cap
            encodage_video = root.find('.//ns0:videoCodecType', namespaces=ns_map).text

            # Trouver les éléments <enabled> dans différents espaces de noms
            motion_elements_ns0 = root.findall('.//ns0:MotionDetection/ns0:enabled', namespaces=ns_map)
            motion_elements_ns1 = root.findall('.//ns1:MotionDetection/ns1:enabled', namespaces=ns_map)

            if motion_elements_ns0:
                motion_enabled = motion_elements_ns0[0].text
            elif motion_elements_ns1:
                motion_enabled = motion_elements_ns1[0].text
            else:
                motion_enabled = 'false'  # ou toute valeur par défaut que vous souhaitez

            encrypt_elements_ns0 = root.findall('.//ns0:EZVIZ/ns0:enabled', namespaces=ns_map)
            encrypt_elements_ns2 = root.findall('.//ns2:EZVIZ/ns2:enabled', namespaces=ns_map)

            if encrypt_elements_ns0:
                encrypt_enabled = encrypt_elements_ns0[0].text
            elif encrypt_elements_ns2:
                encrypt_enabled = encrypt_elements_ns2[0].text
            else:
                encrypt_enabled = 'false'  # ou toute valeur par défaut que vous souhaitez

            motion_detect = "true" if motion_enabled.lower() == 'true' else "false"
            encrypt = "true" if encrypt_enabled.lower() == 'true' else "false"

            return {
                'id_channel': id_channel,
                'width_resolution': width_resolution,
                'height_resolution': height_resolution,
                'type_bande_passante': type_bande_passante,
                'image_par_sec': image_par_sec,
                'debit_bin_max': debit_bin_max,
                'encodage_video': encodage_video,
                'motion_detect': motion_detect,
                'encrypt': encrypt
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
                fetch_and_parse(f"{channel:02d}01")
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
        xml = re.sub(r"<enabled>.*?</enabled>", "<enabled>true</enabled>", xml)
    else:
        xml = re.sub(r"<enabled>.*?</enabled>", "<enabled>false</enabled>", xml)

    response = requests.put(url, auth=HTTPDigestAuth(username, password), data=xml)
    if response.status_code == 200:
        print(response.status_code)
        print("--------------- PARAMETRE APRES CHANGEMENT ---------------")
        print(xml)
        print("------------------------------")
    else:
        print(f"Erreur : {response.status_code} - {response.text}")

def get_camera_parameters_unique(camera_ip, username, password):
    number=get_param(camera_ip, username, password)
    port=number[1]
    url_image_settings_main = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/101/capabilities'
    url_image_settings_sub = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/102/capabilities'
    url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Security/users/'
    print("Pour IP "+camera_ip)
    response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

    # Vérifier si la requête a réussi
    if response_get.status_code == 200:
        xml = response_get.text
        print(xml)
    else:
        print(f"Erreur : {response_get.status_code} - {response_get.text}")
    tab=[[url_image_settings_main,"primaire"],[url_image_settings_sub,"secondaire"]]
    for t in tab:
        try:
            # Effectuer une requête HTTP GET avec une authentification basique
            response = requests.get(t[0], auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi (code d'état 200)
            if response.status_code == 200:

                xml = response.text
                #print(xml)
                root = ET.fromstring(xml)
                namespace_uri = root.tag.split('}', 1)[0][1:]
                if namespace_uri in ns['ns'] :

                    videoCodecTypeElement = root.find('.//ns:videoCodecType', namespaces=ns)
                    videoCodec_opt = videoCodecTypeElement.attrib['opt']

                    videoResolutionWidth = root.find('.//ns:videoResolutionWidth', namespaces=ns)
                    videoResolutionWidth_opt = videoResolutionWidth.attrib['opt']

                    videoResolutionHeight = root.find('.//ns:videoResolutionHeight', namespaces=ns)
                    videoResolutionHeight_opt = videoResolutionHeight.attrib['opt']

                    maxFrameRate = root.find('.//ns:maxFrameRate', namespaces=ns)
                    maxFrameRate_opt = maxFrameRate.attrib['opt']
                    # Diviser la chaîne en une liste de chaînes
                    string_list = maxFrameRate_opt.split(',')

                    # Convertir chaque élément de la liste en entier
                    int_list = [int(x) for x in string_list]
                    maxFrameRate_opt_list = [x / 100 for x in int_list]
                    maxFrameRate_opt_list.pop(0)

                    constantBitRate = root.find('.//ns:constantBitRate', namespaces=ns)
                    constantBitRate_min = constantBitRate.attrib['min']
                    constantBitRate_max = constantBitRate.attrib['max']
                    constantBitRate_opt={"valeur min ":constantBitRate_min,"valeur max ":constantBitRate_max}
                    print("// Flux "+t[1]+" //")
                    print_settings(videoCodec_opt,videoResolutionWidth_opt,videoResolutionHeight_opt,maxFrameRate_opt_list,constantBitRate_opt)
                    print("---------------------")
                elif  namespace_uri in ns2['xmlns'] :
                    videoCodecTypeElement = root.find('.//xmlns:videoCodecType', namespaces=ns2)
                    videoCodec_opt = videoCodecTypeElement.attrib['opt']

                    videoResolutionWidth = root.find('.//xmlns:videoResolutionWidth', namespaces=ns2)
                    videoResolutionWidth_opt = videoResolutionWidth.attrib['opt']

                    videoResolutionHeight = root.find('.//xmlns:videoResolutionHeight', namespaces=ns2)
                    videoResolutionHeight_opt = videoResolutionHeight.attrib['opt']

                    maxFrameRate = root.find('.//xmlns:maxFrameRate', namespaces=ns2)
                    maxFrameRate_opt = maxFrameRate.attrib['opt']
                    # Diviser la chaîne en une liste de chaînes
                    string_list = maxFrameRate_opt.split(',')

                    # Convertir chaque élément de la liste en entier
                    int_list = [int(x) for x in string_list]
                    maxFrameRate_opt_list = [x / 100 for x in int_list]
                    maxFrameRate_opt_list.pop(0)

                    constantBitRate = root.find('.//xmlns:constantBitRate', namespaces=ns2)
                    constantBitRate_min = constantBitRate.attrib['min']
                    constantBitRate_max = constantBitRate.attrib['max']
                    constantBitRate_opt={"valeur min ":constantBitRate_min,"valeur max ":constantBitRate_max}
                    
                    print("// Flux "+t[1]+" //")
                    print_settings(videoCodec_opt,videoResolutionWidth_opt,videoResolutionHeight_opt,maxFrameRate_opt_list,constantBitRate_opt)
                    print("---------------------")
                elif  namespace_uri in ns3['xmlns'] :
                    videoCodecTypeElement = root.find('.//xmlns:videoCodecType', namespaces=ns3)
                    videoCodec_opt = videoCodecTypeElement.attrib['opt']

                    videoResolutionWidth = root.find('.//xmlns:videoResolutionWidth', namespaces=ns3)
                    videoResolutionWidth_opt = videoResolutionWidth.attrib['opt']

                    videoResolutionHeight = root.find('.//xmlns:videoResolutionHeight', namespaces=ns3)
                    videoResolutionHeight_opt = videoResolutionHeight.attrib['opt']

                    maxFrameRate = root.find('.//xmlns:maxFrameRate', namespaces=ns3)
                    maxFrameRate_opt = maxFrameRate.attrib['opt']
                    # Diviser la chaîne en une liste de chaînes
                    string_list = maxFrameRate_opt.split(',')

                    # Convertir chaque élément de la liste en entier
                    int_list = [int(x) for x in string_list]
                    maxFrameRate_opt_list = [x / 100 for x in int_list]
                    maxFrameRate_opt_list.pop(0)

                    constantBitRate = root.find('.//xmlns:constantBitRate', namespaces=ns3)
                    constantBitRate_min = constantBitRate.attrib['min']
                    constantBitRate_max = constantBitRate.attrib['max']
                    constantBitRate_opt={"valeur min ":constantBitRate_min,"valeur max ":constantBitRate_max}
                    
                    print("// Flux "+t[1]+" //")
                    print_settings(videoCodec_opt,videoResolutionWidth_opt,videoResolutionHeight_opt,maxFrameRate_opt_list,constantBitRate_opt)
                    print("---------------------")
                elif  namespace_uri in ns4['xmlns'] :
                    videoCodecTypeElement = root.find('.//xmlns:videoCodecType', namespaces=ns4)
                    videoCodec_opt = videoCodecTypeElement.attrib['opt']

                    videoResolutionWidth = root.find('.//xmlns:videoResolutionWidth', namespaces=ns4)
                    videoResolutionWidth_opt = videoResolutionWidth.attrib['opt']

                    videoResolutionHeight = root.find('.//xmlns:videoResolutionHeight', namespaces=ns4)
                    videoResolutionHeight_opt = videoResolutionHeight.attrib['opt']

                    maxFrameRate = root.find('.//xmlns:maxFrameRate', namespaces=ns4)
                    maxFrameRate_opt = maxFrameRate.attrib['opt']
                    # Diviser la chaîne en une liste de chaînes
                    string_list = maxFrameRate_opt.split(',')

                    # Convertir chaque élément de la liste en entier
                    int_list = [int(x) for x in string_list]
                    maxFrameRate_opt_list = [x / 100 for x in int_list]
                    maxFrameRate_opt_list.pop(0)

                    constantBitRate = root.find('.//xmlns:constantBitRate', namespaces=ns4)
                    constantBitRate_min = constantBitRate.attrib['min']
                    constantBitRate_max = constantBitRate.attrib['max']
                    constantBitRate_opt={"valeur min ":constantBitRate_min,"valeur max ":constantBitRate_max}
                    
                    print("// Flux "+t[1]+" //")
                    print_settings(videoCodec_opt,videoResolutionWidth_opt,videoResolutionHeight_opt,maxFrameRate_opt_list,constantBitRate_opt)
                    print("---------------------")
                elif  namespace_uri in ns5['xmlns'] :
                    videoCodecTypeElement = root.find('.//xmlns:videoCodecType', namespaces=ns5)
                    videoCodec_opt = videoCodecTypeElement.attrib['opt']

                    videoResolutionWidth = root.find('.//xmlns:videoResolutionWidth', namespaces=ns5)
                    videoResolutionWidth_opt = videoResolutionWidth.attrib['opt']

                    videoResolutionHeight = root.find('.//xmlns:videoResolutionHeight', namespaces=ns5)
                    videoResolutionHeight_opt = videoResolutionHeight.attrib['opt']

                    maxFrameRate = root.find('.//xmlns:maxFrameRate', namespaces=ns5)
                    maxFrameRate_opt = maxFrameRate.attrib['opt']
                    # Diviser la chaîne en une liste de chaînes
                    string_list = maxFrameRate_opt.split(',')

                    # Convertir chaque élément de la liste en entier
                    int_list = [int(x) for x in string_list]
                    maxFrameRate_opt_list = [x / 100 for x in int_list]
                    maxFrameRate_opt_list.pop(0)

                    constantBitRate = root.find('.//xmlns:constantBitRate', namespaces=ns5)
                    constantBitRate_min = constantBitRate.attrib['min']
                    constantBitRate_max = constantBitRate.attrib['max']
                    constantBitRate_opt={"valeur min ":constantBitRate_min,"valeur max ":constantBitRate_max}
                    
                    print("// Flux "+t[1]+" //")
                    print_settings(videoCodec_opt,videoResolutionWidth_opt,videoResolutionHeight_opt,maxFrameRate_opt_list,constantBitRate_opt)
                    print("---------------------")
                elif  namespace_uri in ns6['xmlns'] :
                    videoCodecTypeElement = root.find('.//xmlns:videoCodecType', namespaces=ns6)
                    videoCodec_opt = videoCodecTypeElement.attrib['opt']

                    videoResolutionWidth = root.find('.//xmlns:videoResolutionWidth', namespaces=ns6)
                    videoResolutionWidth_opt = videoResolutionWidth.attrib['opt']

                    videoResolutionHeight = root.find('.//xmlns:videoResolutionHeight', namespaces=ns6)
                    videoResolutionHeight_opt = videoResolutionHeight.attrib['opt']

                    maxFrameRate = root.find('.//xmlns:maxFrameRate', namespaces=ns6)
                    maxFrameRate_opt = maxFrameRate.attrib['opt']
                    # Diviser la chaîne en une liste de chaînes
                    string_list = maxFrameRate_opt.split(',')

                    # Convertir chaque élément de la liste en entier
                    int_list = [int(x) for x in string_list]
                    maxFrameRate_opt_list = [x / 100 for x in int_list]
                    maxFrameRate_opt_list.pop(0)

                    constantBitRate = root.find('.//xmlns:constantBitRate', namespaces=ns6)
                    constantBitRate_min = constantBitRate.attrib['min']
                    constantBitRate_max = constantBitRate.attrib['max']
                    constantBitRate_opt={"valeur min ":constantBitRate_min,"valeur max ":constantBitRate_max}
                    
                    print("// Flux "+t[1]+" //")
                    print_settings(videoCodec_opt,videoResolutionWidth_opt,videoResolutionHeight_opt,maxFrameRate_opt_list,constantBitRate_opt)
                    print("---------------------")
            else:
                print(f"Erreur : {response.status_code} - {response.text}")

        except requests.RequestException as e:
            print(f"Erreur de requête : {e}")


    
def get_param(camera_ip, username, password):
    # Tentative sur le port 80
    port = 80
    url_image_settings = f'http://{camera_ip}:{port}/ISAPI/System/Video/inputs/channels/'
    try:
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
        print(f"Tentative sur le port 80: {response_get.status_code}")
        
        if response_get.status_code == 200:
            xml = response_get.text
            match = re.search(r"<inputPort>(\d+)</inputPort>(?:(?!<inputPort>).)*$", xml, re.DOTALL)
            if match:
                valeur_input_port = match.group(1)
                print(f"Port 80 fonctionnel, {valeur_input_port} caméras détectées.")
                return [valeur_input_port, str(port)]
            else:
                print("Pas de valeur trouvée pour <inputPort> sur le port 80, retour à 30 caméras.")
                return [30, str(port)]
        else:
            print(f"Port 80 non utilisable avec code de retour: {response_get.status_code}")
    except requests.exceptions.ConnectionError:
        print("Port 80 fermé ou inaccessible.")

    # Si le port 80 échoue, vérification avec /ISAPI/Streaming/channels/101
    url_test = f'http://{camera_ip}:{port}/ISAPI/Security/users/'
    try:
        response_test = requests.get(url_test, auth=HTTPDigestAuth(username, password))
        if response_test.status_code == 200:
            print(f"Port {port} validé avec le test sur /ISAPI/Security/users/ ")
            return [30, str(port)]
        else:
            print(f"Port {port} non valide, réponse {response_test.status_code} pour /ISAPI/Security/users/ ")
    except requests.exceptions.ConnectionError:
        print(f"Port {port} fermé ou inaccessible lors du test sur /ISAPI/Security/users/ ")

    # Si le port 80 échoue, scannez les autres ports
    open_ports = scan_ports(camera_ip)
    print("Ports ouverts détectés:", open_ports)

    for port in open_ports:
        url_test = f'http://{camera_ip}:{port}/ISAPI/Security/users/'
        try:
            response_test = requests.get(url_test, auth=HTTPDigestAuth(username, password))
            if response_test.status_code == 200:
                print(f"Port {port} validé avec le test sur /ISAPI/Security/users/ ")
                return [30, str(port)]
        except requests.exceptions.ConnectionError:
            print(f"Port {port} fermé ou inaccessible lors du test sur /ISAPI/Security/users/ ")
    
    print("Aucun port n'a répondu correctement.")
    return [30, str(port)]



def set_motion(camera_ip, username, password, channel_id, motionDetect, cam):
    number = get_param(camera_ip, username, password)
    port = number[1]
    nbCam = int(number[0])
    if cam == "yes":
        nbCam = 1
    if "all" in channel_id:
        for x in range(nbCam):
            print(x + 1)
            channel2 = x + 1
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/System/Video/inputs/channels/{channel2}/MotionDetection'
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
            print(url_image_settings)
            if response_get.status_code == 200:
                xml = response_get.text
                print(xml)
                print("------------------------------")
                xml = re.sub(r"<enabled>.*?</enabled>", f"<enabled>{motionDetect.lower()}</enabled>", xml)
                response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
                if response.status_code == 200:
                    print(f"Detection mouvement pour camera {channel2} mise à {motionDetect.lower()}")
                else:
                    print(f"Erreur : {response.status_code} - {response.text}")
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")
    else:
        url_image_settings = f'http://{camera_ip}:{port}/ISAPI/System/Video/inputs/channels/{channel_id}/MotionDetection'
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))
        print(url_image_settings)
        if response_get.status_code == 200:
            xml = response_get.text
            xml = re.sub(r"<enabled>.*?</enabled>", f"<enabled>{motionDetect.lower()}</enabled>", xml)
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)
            if response.status_code == 200:
                print(f"Detection mouvement pour camera {channel_id} mise à {motionDetect.lower()}")
            else:
                print(f"Erreur : {response.status_code} - {response.text}")
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")


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

def print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video,motion_detect,encrypt):
    print('ID Channel :', id_channel)
    print('Resolution : ', str(width_resolution)+"x"+str(height_resolution))
    print('Type bande passante : ', type_bande_passante)
    if int(image_par_sec)==0:
        print('Image par seconde : MAX fps')
    else:
        print('Image par seconde : ', int(image_par_sec)/100 ,' fps')
        print('Debit binaire max : ', debit_bin_max)
        print('Encodage vidéo : ', encodage_video)
        print('Motion Detect : ',motion_detect)
        print('Encrypt : ',encrypt.lower())

def print_settings(videoCodec_opt,videoResolutionWidth_opt,videoResolutionHeight_opt,maxFrameRate_opt_list,constantBitRate_opt):
    print('Compression :', videoCodec_opt)
    # Séparer les chaînes de caractères en listes
    widths = str(videoResolutionWidth_opt).split(',')
    heights = str(videoResolutionHeight_opt).split(',')
    # Associer chaque largeur avec sa hauteur correspondante
    resolutions = [f"{w}x{h}" for w, h in zip(widths, heights)]
    # Convertir la liste de résolutions formatées en une chaîne de caractères
    formatted_resolutions = ','.join(resolutions)
    print('Resolution :', formatted_resolutions)
    print('FPSMax :', maxFrameRate_opt_list)
    print('BitRate :', constantBitRate_opt)

    
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
    parser.add_argument("--encrypt", type=str, required=False)
    parser.add_argument("--country", type=str, required=False)
    parser.add_argument("--app", action="store_true", required=False)
    parser.add_argument("--reboot", action="store_true", required=False)

    args = parser.parse_args(args)
    if "{" in args.ip and not args.app:
            print("update")
            print("camera ip")
            ip_list = expand_ip_range(args.ip)
            print(ip_list)
            for ip in ip_list:
                    print("***")
                    print("Camera : "+str(ip.split(".")[3]))
                    if args.u!=None and args.p!=None and ip!=None and args.reboot:
                        print("reboot")
                        reboot_dvr(ip, args.u, args.p)
                        return
                    if args.ch is None and args.r is None and args.f is None and args.b is None and args.c is None and args.m is None and not args.reboot:
                        get_camera_parameters_unique(ip, args.u, args.p)
                        return
                    if args.country!=None:
                        setTime(ip, args.u, args.p, args.country)
                        return
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
                    if args.ch!=None and not args.app and args.r is None and args.f is None and args.b is None and args.c is None and args.m is None:
                        get_camera_parameters(ip, args.u, args.p, args.ch,"yes")
                    if args.bc!=None:
                        set_bitrateControl(ip, args.u, args.p, args.ch, args.bc, "yes")
                    print("fin") 
            print("possibility to display : ")
            get_camera_parameters_unique(ip_list[0], args.u, args.p)
    elif "{"  not in args.ip and args.app :  
                print("display") 
                get_camera_parameters(args.ip, args.u, args.p, "all_main","no")
                get_camera_parameters(args.ip, args.u, args.p, "all_sub","no")
                print("possibility to display : ")
                get_camera_parameters_unique(args.ip, args.u, args.p)
    elif "{" in args.ip and args.app :  
                print("display")
                print("camera ip")
                ip_list = expand_ip_range(args.ip)
                print(ip_list)
                for ip in ip_list:
                    print("***")
                    print("Camera : "+str(ip.split(".")[3]))
                    get_camera_parameters(ip, args.u, args.p, "all_main","yes")
                    get_camera_parameters(ip, args.u, args.p, "all_sub","yes")
                print("possibility to display : ")
                get_camera_parameters_unique(ip_list[0], args.u, args.p)
    else:
            print("update")
            if args.u!=None and args.p!=None and args.ip!=None and args.reboot:
                print("reboot")
                reboot_dvr(args.ip, args.u, args.p)
                return
            if args.ch is None and args.r is None and args.f is None and args.b is None and args.c is None and args.m is None and not args.reboot:
                get_camera_parameters_unique(args.ip, args.u, args.p)
                return
            if args.country!=None:
                setTime(args.ip, args.u, args.p, args.country)
                return
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
            if args.ch!=None and not args.app and args.r is None and args.f is None and args.b is None and args.c is None and args.m is None:
                get_camera_parameters(args.ip, args.u, args.p, args.ch,"no")
            if args.bc!=None:
                set_bitrateControl(args.ip, args.u, args.p, args.ch, args.bc, "no")
            if args.encrypt!=None:
                encryption(args.ip, args.u, args.p, args.encrypt)
            print("fin")
            print("possibility to display : ")
            get_camera_parameters_unique(args.ip, args.u, args.p)


if __name__ == "__main__":

    main()

