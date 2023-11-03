import requests
from requests.auth import HTTPDigestAuth
import re
import argparse
import xml.etree.ElementTree as ET


def set_resolution(camera_ip, username, password, channel_id, resolution_width, resolution_height):
    # Remplacez ces valeurs par celles de votre caméra
    camera_ip = camera_ip
    username = username
    password = password
    channel_id = channel_id
    resolution_width = resolution_width
    resolution_height = resolution_height

    # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
    url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel_id}'

    # Effectuer une requête HTTP GET
    response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

    # Vérifier si la requête a réussi
    if response_get.status_code == 200:
        xml = response_get.text
        print(xml)
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


def set_fps(camera_ip, username, password, channel_id, fps):
    # Remplacez ces valeurs par celles de votre caméra
    camera_ip = camera_ip
    username = username
    password = password
    channel_id = channel_id
    fps=fps

    # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
    url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel_id}'

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
        print("La résolution a été modifiée avec succès.")
        #print(response_put.text)
    else:
        print(f"Erreur : {response_put.status_code} - {response_put.text}")

def set_bitrate(camera_ip, username, password, channel_id, BitRate):
  
    # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
    url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel_id}'

    # Effectuer une requête HTTP GET
    response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

    # Vérifier si la requête a réussi
    if response_get.status_code == 200:
        xml = response_get.text
        print(xml)
    else:
        print(f"Erreur : {response_get.status_code} - {response_get.text}")
        return

    # Modifier la résolution
    try:
        xml = re.sub(r"<constantBitRate>.*?</constantBitRate>", f"<constantBitRate>{BitRate}</constantBitRate>", xml)
    except:
        xml = re.sub(r"<vbrUpperCap>.*?</vbrUpperCap>", f"<vbrUpperCap>{BitRate}</vbrUpperCap>", xml)

    # Effectuer la requête HTTP PUT
    response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        print("La résolution a été modifiée avec succès.")
    else:
        print(f"Erreur : {response.status_code} - {response.text}")





def get_camera_parameters(camera_ip, username, password, channel_id):
    url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel_id}/'

    try:
        # Effectuer une requête HTTP GET avec une authentification basique
        response = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

        # Vérifier si la requête a réussi (code d'état 200)
        if response.status_code == 200:
            xml = response.text
            print(xml)
            root = ET.fromstring(xml)

            # Espaces de noms XML
            ns = {'ns': 'http://www.hikvision.com/ver20/XMLSchema'}

            id_channel = root.find('.//ns:channelName', namespaces=ns).text
            width_resolution = root.find('.//ns:videoResolutionWidth', namespaces=ns).text
            height_resolution = root.find('.//ns:videoResolutionHeight', namespaces=ns).text
            try :
                constant_bit_rate = root.find('.//ns:constantBitRate', namespaces=ns)
            except :
                constant_bit_rate = None   

            try : 
                vbr_Upper_Cap =  root.find('.//ns:vbrUpperCap', namespaces=ns)
            except : 
                vbr_Upper_Cap =  None
            type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
            image_par_sec = root.find('.//ns:maxFrameRate', namespaces=ns).text
            try :
                debit_bin_max = constant_bit_rate.text 
            except : 
                debit_bin_max = vbr_Upper_Cap.text    
            encodage_video = root.find('.//ns:videoCodecType', namespaces=ns).text

            print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video)

        else:
            print(f"Erreur : {response.status_code} - {response.text}")

    except requests.RequestException as e:
        print(f"Erreur de requête : {e}")
def print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video):
    print('ID Channel :', id_channel)
    print('Width resolution : ', width_resolution)
    print('Height resolution : ', height_resolution)
    print('Type bande passante : ', type_bande_passante)
    print('Image par seconde : ', int(image_par_sec)/100 ,' fps')
    print('Debit binaire max : ', debit_bin_max)
    print('Encodage_video : ', encodage_video)
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--camera_ip", type=str, required=True)
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--password", type=str, required=True)
    parser.add_argument("--channel_id", type=int, required=True)
    parser.add_argument("--resolution_width", type=int, required=False)
    parser.add_argument("--resolution_height", type=int, required=False)
    parser.add_argument("--fps", type=int, required=False)
    parser.add_argument("--bitrate", type=int, required=False)
    args = parser.parse_args()
    if args.resolution_width!=None:
        set_resolution(args.camera_ip, args.username, args.password, args.channel_id, args.resolution_width, args.resolution_height)
    if args.fps!=None:
        set_fps(args.camera_ip, args.username, args.password, args.channel_id, args.fps)
    if args.bitrate!=None:
        set_bitrate(args.camera_ip, args.username, args.password, args.channel_id, args.bitrate)
    else:
        get_camera_parameters(args.camera_ip, args.username, args.password, args.channel_id)

#python3 test_python_http.py --camera_ip 172.24.24.126 --username admin --password Hikvision --channel_id 102 --resolution_width 320 --resolution_height 240