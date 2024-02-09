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
        
   

## MODIF RESOLUTION CAM FLUX PRIMAIRE OU SECONDAIRE
def set_resolution(camera_ip, username, password, channel_id, resolution,cam):
    resolution_width = resolution.split("x")[0]
    resolution_height = resolution.split("x")[1]
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
           
            # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}'
            #print(url_image_settings)

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")

            # Modifier la résolution

            
            # Modifier le fps
            xml = re.sub(r"<videoResolutionWidth>.*?</videoResolutionWidth>", f"<videoResolutionWidth>{resolution_width}</videoResolutionWidth>", xml)
            xml = re.sub(r"<videoResolutionHeight>.*?</videoResolutionHeight>", f"<videoResolutionHeight>{resolution_height}</videoResolutionHeight>", xml)

            # Effectuer la requête HTTP PUT
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

            # Vérifier si la requête a réussi
            if response.status_code == 200:
                print("Resolution pour camera "+str(channel2)+" mise à "+str(resolution)) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")
    else:

        resolution_width = resolution.split("x")[0]
        resolution_height = resolution.split("x")[1]

        # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
        url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel_id}'

        # Effectuer une requête HTTP GET
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

        # Vérifier si la requête a réussi
        if response_get.status_code == 200:
            xml = response_get.text
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")

        # Modifier la résolution

        xml = re.sub(r"<videoResolutionWidth>.*?</videoResolutionWidth>", f"<videoResolutionWidth>{resolution_width}</videoResolutionWidth>", xml)
        xml = re.sub(r"<videoResolutionHeight>.*?</videoResolutionHeight>", f"<videoResolutionHeight>{resolution_height}</videoResolutionHeight>", xml)
        # Effectuer la requête HTTP PUT
        response_put = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

        # Vérifier si la requête a réussi
        if response_put.status_code == 200:
            print("La résolution a été modifiée avec succès.")
            #print(response_put.text)
        else:
            print(f"Erreur : {response_put.status_code} - {response_put.text}")


## MODIF FPS CAM ##
def set_fps(camera_ip, username, password, channel_id, fps,cam):
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
            # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}'
            #print(url_image_settings)

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")

            # Modifier la résolution

            
            # Modifier le fps
            xml = re.sub(r"<maxFrameRate>.*?</maxFrameRate>", f"<maxFrameRate>{fps*100}</maxFrameRate>", xml)

            # Effectuer la requête HTTP PUT
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

            # Vérifier si la requête a réussi
            if response.status_code == 200:
                print("Fps pour camera "+str(channel2)+" mise à "+str(fps)) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")
    else:


        # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
        url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel_id}'

        # Effectuer une requête HTTP GET
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

        # Vérifier si la requête a réussi
        if response_get.status_code == 200:
            xml = response_get.text
            print(xml)
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")

        # Modifier la résolution

        xml = re.sub(r"<maxFrameRate>.*?</maxFrameRate>", f"<maxFrameRate>{fps*100}</maxFrameRate>", xml)
        # Effectuer la requête HTTP PUT
        response_put = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

        # Vérifier si la requête a réussi
        if response_put.status_code == 200:
            print("Les fps ont été modifiée avec succès.")
            #print(response_put.text)
        else:
            print(f"Erreur : {response_put.status_code} - {response_put.text}")


## MODIF BITREATE CAM ##
def set_bitrate(camera_ip, username, password, channel_id, BitRate,cam):
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
            # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}'
            #print(url_image_settings)

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")

            # Modifier la résolution

            
            # Modifier le bitrate
            try:
                xml = re.sub(r"<constantBitRate>.*?</constantBitRate>", f"<constantBitRate>{BitRate}</constantBitRate>", xml)
            except:
                xml = re.sub(r"<vbrUpperCap>.*?</vbrUpperCap>", f"<vbrUpperCap>{BitRate}</vbrUpperCap>", xml)

            # Effectuer la requête HTTP PUT
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

            # Vérifier si la requête a réussi
            if response.status_code == 200:
                print("Bitrate pour camera "+str(channel2)+" mise à "+str(BitRate)) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")
    else:
  
        # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
        url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel_id}'

        # Effectuer une requête HTTP GET
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

        # Vérifier si la requête a réussi
        if response_get.status_code == 200:
            xml = response_get.text
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")

        # Modifier le bitrate
        try:
            xml = re.sub(r"<constantBitRate>.*?</constantBitRate>", f"<constantBitRate>{BitRate}</constantBitRate>", xml)
        except:
            xml = re.sub(r"<vbrUpperCap>.*?</vbrUpperCap>", f"<vbrUpperCap>{BitRate}</vbrUpperCap>", xml)

        # Effectuer la requête HTTP PUT
        response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

        # Vérifier si la requête a réussi
        if response.status_code == 200:
            print("Le bitrate a été modifiée avec succès.")
        else:
            print(f"Erreur : {response.status_code} - {response.text}")
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
            # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}'
            #print(url_image_settings)

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")

            # Modifier la résolution

            xml = re.sub(r"<videoCodecType>.*?</videoCodecType>", f"<videoCodecType>{compression}</videoCodecType>", xml)

            # Effectuer la requête HTTP PUT
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

            # Vérifier si la requête a réussi
            if response.status_code == 200:
                print("Compression pour camera "+str(channel2)+" mise à "+compression) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")
    else:
            # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel_id}'

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")

            # Modifier la résolution

            xml = re.sub(r"<videoCodecType>.*?</videoCodecType>", f"<videoCodecType>{compression}</videoCodecType>", xml)

            # Effectuer la requête HTTP PUT
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

            # Vérifier si la requête a réussi
            if response.status_code == 200:
                print("Compression pour camera "+str(channel_id)+" mise à "+compression) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")



## Recuperer parametres globaux flux vidéo secondaire ou primaire ##
def get_camera_parameters(camera_ip, username, password, channel_id,cam):
    number=get_param(camera_ip, username, password)
    port=number[1]
    nbCam=int(number[0])
    if cam == "yes":
        nbCam = 1
    # Espaces de noms XML
    if "all"in channel_id:
        for x in range(nbCam):
            print(x+1)
            if channel_id=="all_main":
                channel=x+1
                channel2=str(channel)+"01"
            elif channel_id=="all_sub":
                channel=x+1
                channel2=str(channel)+"02"
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel2}/'

            try:
                # Effectuer une requête HTTP GET avec une authentification basique
                response = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

                # Vérifier si la requête a réussi (code d'état 200)
                if response.status_code == 200:
                    xml = response.text
                    #print(xml)
                    root = ET.fromstring(xml)
                    namespace_uri = root.tag.split('}', 1)[0][1:]
 
                    if namespace_uri in ns['ns'] :
                        id_channel = root.find('.//ns:channelName', namespaces=ns).text
                        width_resolution = root.find('.//ns:videoResolutionWidth', namespaces=ns).text
                        height_resolution = root.find('.//ns:videoResolutionHeight', namespaces=ns).text
                       
                        image_par_sec = root.find('.//ns:maxFrameRate', namespaces=ns).text
                        
                        try:
                            constant_bit_rate = root.find('.//ns:constantBitRate', namespaces=ns).text
                        except:
                            constant_bit_rate = None
                        type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                        try:
                            vbr_Upper_Cap =  root.find('.//ns:vbrUpperCap', namespaces=ns).text
                        except:
                            vbr_Upper_Cap =  None
                        if constant_bit_rate!= None:
                            debit_bin_max = constant_bit_rate 
                        else:
                            debit_bin_max = vbr_Upper_Cap  
                        encodage_video = root.find('.//ns:videoCodecType', namespaces=ns).text
                    elif  namespace_uri in ns2['xmlns'] :
                        id_channel = root.find('.//xmlns:channelName', namespaces=ns2).text
                        width_resolution = root.find('.//xmlns:videoResolutionWidth', namespaces=ns2).text
                        height_resolution = root.find('.//xmlns:videoResolutionHeight', namespaces=ns2).text
                        
                        image_par_sec = root.find('.//xmlns:maxFrameRate', namespaces=ns2).text
                        
                        try:
                            constant_bit_rate = root.find('.//xmlns:constantBitRate', namespaces=ns2).text
                        except:
                            constant_bit_rate = None
                        type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                        try:
                            vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns2).text
                        except:
                            vbr_Upper_Cap =  None
                        try :
                            debit_bin_max = constant_bit_rate
                        except : 
                            debit_bin_max = vbr_Upper_Cap   
                        encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns2).text
                    elif  namespace_uri in ns3['xmlns'] :
                        id_channel = root.find('.//xmlns:channelName', namespaces=ns3).text
                        width_resolution = root.find('.//xmlns:videoResolutionWidth', namespaces=ns3).text
                        height_resolution = root.find('.//xmlns:videoResolutionHeight', namespaces=ns3).text
                        
                        image_par_sec = root.find('.//xmlns:maxFrameRate', namespaces=ns3).text
                        
                        try:
                            constant_bit_rate = root.find('.//xmlns:constantBitRate', namespaces=ns3).text
                        except:
                            constant_bit_rate = None
                        type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                        try:
                            vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns3).text
                        except:
                            vbr_Upper_Cap =  None
                        try :
                            debit_bin_max = constant_bit_rate 
                        except : 
                            debit_bin_max = vbr_Upper_Cap   
                        encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns3).text
                    elif  namespace_uri in ns4['xmlns'] :
                        id_channel = root.find('.//xmlns:channelName', namespaces=ns4).text
                        width_resolution = root.find('.//xmlns:videoResolutionWidth', namespaces=ns4).text
                        height_resolution = root.find('.//xmlns:videoResolutionHeight', namespaces=ns4).text
                        
                        image_par_sec = root.find('.//xmlns:maxFrameRate', namespaces=ns4).text
                        
                        try:
                            constant_bit_rate = root.find('.//xmlns:constantBitRate', namespaces=ns4).text
                        except:
                            constant_bit_rate = None
                        type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                        try:
                            vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns4).text
                        except:
                            vbr_Upper_Cap =  None
                        try :
                            debit_bin_max = constant_bit_rate 
                        except : 
                            debit_bin_max = vbr_Upper_Cap    
                        encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns4).text
                    elif  namespace_uri in ns6['xmlns'] :
                        id_channel = root.find('.//xmlns:channelName', namespaces=ns6).text
                        width_resolution = root.find('.//xmlns:videoResolutionWidth', namespaces=ns6).text
                        height_resolution = root.find('.//xmlns:videoResolutionHeight', namespaces=ns6).text
                        
                        image_par_sec = root.find('.//xmlns:maxFrameRate', namespaces=ns6).text
                        
                        try:
                            constant_bit_rate = root.find('.//xmlns:constantBitRate', namespaces=ns6).text
                        except:
                            constant_bit_rate = None
                        type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                        try:
                            vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns6).text
                        except:
                            vbr_Upper_Cap =  None
                        try :
                            debit_bin_max = constant_bit_rate 
                        except : 
                            debit_bin_max = vbr_Upper_Cap    
                        encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns6).text

                    print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video)
                    print("-----------")
                else:
                    print(f"Erreur : {response.status_code} - {response.text}")

            except requests.RequestException as e:
                print(f"Erreur de requête : {e}")
    else:
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/Streaming/channels/{channel_id}/'

            try:
                # Effectuer une requête HTTP GET avec une authentification basique
                response = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

                # Vérifier si la requête a réussi (code d'état 200)
                if response.status_code == 200:
                    xml = response.text
                    #print(xml)
                    root = ET.fromstring(xml)
                    namespace_uri = root.tag.split('}', 1)[0][1:]

                    if namespace_uri in ns['ns'] :
                        try:
                            id_channel = root.find('.//ns:channelName', namespaces=ns).text
                            width_resolution = root.find('.//ns:videoResolutionWidth', namespaces=ns).text
                            height_resolution = root.find('.//ns:videoResolutionHeight', namespaces=ns).text
                            try :
                                constant_bit_rate = root.find('.//ns:constantBitRate', namespaces=ns).text
                            except :
                                constant_bit_rate = None   

                            try : 
                                vbr_Upper_Cap =  root.find('.//ns:vbrUpperCap', namespaces=ns).text
                            except : 
                                vbr_Upper_Cap =  None
                            type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                            image_par_sec = root.find('.//ns:maxFrameRate', namespaces=ns).text
                            try :
                                debit_bin_max = constant_bit_rate
                            except : 
                                debit_bin_max = vbr_Upper_Cap    
                            encodage_video = root.find('.//ns:videoCodecType', namespaces=ns).text

                            print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video)
                            print("-----------")
                        except:
                            print(xml)
                    elif  namespace_uri in ns2['xmlns'] :
                        try:
                            id_channel = root.find('.//xmlns:channelName', namespaces=ns2).text
                            width_resolution = root.find('.//xmlns:videoResolutionWidth', namespaces=ns2).text
                            height_resolution = root.find('.//xmlns:videoResolutionHeight', namespaces=ns2).text
                            try :
                                constant_bit_rate = root.find('.//xmlns:constantBitRate', namespaces=ns2).text
                            except :
                                constant_bit_rate = None   

                            try : 
                                vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns2).text
                            except : 
                                vbr_Upper_Cap =  None
                            type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                            image_par_sec = root.find('.//xmlns:maxFrameRate', namespaces=ns2).text
                            try :
                                debit_bin_max = constant_bit_rate 
                            except : 
                                debit_bin_max = vbr_Upper_Cap    
                            encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns2).text

                            print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video)
                            print("-----------")
                        except:
                            print(xml)
                    elif  namespace_uri in ns3['xmlns'] :
                        try:
                            id_channel = root.find('.//xmlns:channelName', namespaces=ns3).text
                            width_resolution = root.find('.//xmlns:videoResolutionWidth', namespaces=ns3).text
                            height_resolution = root.find('.//xmlns:videoResolutionHeight', namespaces=ns3).text
                            try :
                                constant_bit_rate = root.find('.//xmlns:constantBitRate', namespaces=ns3).text
                            except :
                                constant_bit_rate = None   

                            try : 
                                vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns3).text
                            except : 
                                vbr_Upper_Cap =  None
                            type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                            image_par_sec = root.find('.//xmlns:maxFrameRate', namespaces=ns3).text
                            try :
                                debit_bin_max = constant_bit_rate
                            except : 
                                debit_bin_max = vbr_Upper_Cap    
                            encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns3).text

                            print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video)
                            print("-----------")
                        except:
                            print(xml)
                    elif  namespace_uri in ns4['xmlns'] :
                        try:
                            id_channel = root.find('.//xmlns:channelName', namespaces=ns4).text
                            width_resolution = root.find('.//xmlns:videoResolutionWidth', namespaces=ns4).text
                            height_resolution = root.find('.//xmlns:videoResolutionHeight', namespaces=ns4).text
                            try :
                                constant_bit_rate = root.find('.//xmlns:constantBitRate', namespaces=ns4).text
                            except :
                                constant_bit_rate = None   

                            try : 
                                vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns4).text
                            except : 
                                vbr_Upper_Cap =  None
                            type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                            image_par_sec = root.find('.//xmlns:maxFrameRate', namespaces=ns4).text
                            try :
                                debit_bin_max = constant_bit_rate 
                            except : 
                                debit_bin_max = vbr_Upper_Cap    
                            encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns4).text

                            print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video)
                            print("-----------")
                        except:
                            print(xml)
                else:
                    print(f"Erreur : {response.status_code} - {response.text}")

            except requests.RequestException as e:
                print(f"Erreur de requête : {e}")
#Info reseaux y compris acces à la plateforme
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

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        xml = response.text
        print("--------------- PARAMETRE AVANT CHANGEMENT ---------------" )
        print(xml)
        print("------------------------------")
    else:
        print(f"Erreur : {response.status_code} - {response.text}")
        return
    # Modifier la résolution
    if param.lower() =="true":
        xml = re.sub(r"<enabled>.*?</enabled>", f"<enabled>true</enabled>", xml)
    else:
        xml = re.sub(r"<enabled>.*?</enabled>", f"<enabled>false</enabled>", xml)

    # Effectuer la requête HTTP PUT
    response = requests.put(url, auth=HTTPDigestAuth(username, password), data=xml)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        print(response.status_code)
        print("--------------- PARAMETRE APRES CHANGEMENT ---------------")
        print(xml)
        print("------------------------------")
    else:
        print(f"Erreur : {response.status_code} - {response.text}")

## Recuperer liste parametres flux vidéo secondaire ou primaire ##       
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
    open_ports=scan_ports(camera_ip)
    print(open_ports)
    potential_http_ports = []


    for port in open_ports:
        try:
            if is_http_port(camera_ip, username, password, port):
                potential_http_ports.append(port)
                break  # Sortir de la boucle dès qu'un port HTTP potentiel est trouvé
        except:
            print(f"L'itération pour le port {port} a pris trop de temps (plus de 30 secondes).")
            # Ajoutez ici un code pour gérer le dépassement du temps, si nécessaire

    # for port in open_ports:
    #     if is_http_port(camera_ip, username, password, port):
    #         potential_http_ports.append(port)
    #         break  # Sortir de la boucle dès qu'un port HTTP potentiel est trouvé

    #potential_http_ports = [port for port in open_ports if is_http_port(camera_ip, username, password, port)]

    if potential_http_ports:
        print(f"Le ports HTTP potentiel est: {potential_http_ports[0]}")
    else:
        print("Aucun port HTTP potentiel trouvé.")
    # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
    url_image_settings = f'http://{camera_ip}:{port}/ISAPI/System/Video/inputs/channels/'
    #url_image_settings = f'http://{camera_ip}/ISAPI/System/Video/inputs/channels/2/MotionDetection'
    

    # Effectuer une requête HTTP GET
    response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

    # Vérifier si la requête a réussi
    if response_get.status_code == 200:
        xml = response_get.text
        
        namespace = {'ns': 'http://www.hikvision.com/ver20/XMLSchema'}
        root = ET.fromstring(xml)
        # Utiliser re.search pour extraire la valeur de inputPort pour le dernier VideoInputChannel
        match = re.search(r"<inputPort>(\d+)</inputPort>(?:(?!<inputPort>).)*$", xml, re.DOTALL)
        
        if match:
            valeur_input_port = match.group(1)
            #print("Valeur de inputPort pour le dernier VideoInputChannel :", valeur_input_port)
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
    # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
    if "all" in channel_id:
       
        for x in range(nbCam):
            print(x+1)
            if channel_id=="all_main":
                channel2=x+1
            elif channel_id=="all_sub":
                channel2=x+1
            url_image_settings = f'http://{camera_ip}:{port}/ISAPI/System/Video/inputs/channels/{channel2}/MotionDetection'

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
                print(xml)
                print("------------------------------")
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")

            # Modifier la résolution

            xml = re.sub(r"<enabled>.*?</enabled>", f"<enabled>{motionDetect.lower()}</enabled>", xml)

            # Effectuer la requête HTTP PUT
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

            # Vérifier si la requête a réussi
            if response.status_code == 200:
                #print(response.text)
                print("Detection mouvement pour camera "+str(channel_id)+" mise à "+motionDetect.lower()) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")

                set_motion(camera_ip, username, password, channel_id, motionDetect)
    else:
        url_image_settings = f'http://{camera_ip}:{port}/ISAPI/System/Video/inputs/channels/{channel_id}/MotionDetection'

        # Effectuer une requête HTTP GET
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

        # Vérifier si la requête a réussi
        if response_get.status_code == 200:
            xml = response_get.text
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")

        # Modifier la résolution

        xml = re.sub(r"<enabled>.*?</enabled>", f"<enabled>{motionDetect.lower()}</enabled>", xml)

        # Effectuer la requête HTTP PUT
        response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

        # Vérifier si la requête a réussi
        if response.status_code == 200:
            #print(response.text)
            print("Detection mouvement pour camera "+str(channel_id)+" mise à "+motionDetect.lower()) 
        else:
            print(f"Erreur : {response.status_code} - {response.text}")


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
    parser.add_argument("--encrypt", type=str, required=False)

    args = parser.parse_args()
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
                if args.ch!=None and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None:
                    get_camera_parameters(ip, args.u, args.p, args.ch,"yes")
                if args.ch==None and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None:
                    get_camera_parameters_unique(ip, args.u, args.p)
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
        if args.ch!=None and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None:
            get_camera_parameters(args.ip, args.u, args.p, args.ch,"no")
        if args.ch==None and args.r==None and args.f==None and args.b==None and args.c==None and args.m==None:
            get_camera_parameters_unique(args.ip, args.u, args.p)


## exemple commande Liste parametres flux primaire ou secondaire##
#python3 update_settings_dvr.py --camera_ip 172.24.1.105 --username admin --password Hikvision --channel_id 102

## exemple commande PUT parametres flux primaire ou secondaire##
##python3 update_settings_dvr.py --camera_ip 172.24.1.105 --username admin --password Hikvision --channel_id 102 --resolution 960x576

#Cryptage du flux de caméra HIK
#supp analyse mouvement HIK DAHUA
