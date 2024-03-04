import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import sys
import argparse

from datetime import datetime
import pytz






def extract_stream_data(xml_str, stream):
   
    # Parser le XML
    root = ET.fromstring(xml_str)

    if(stream =="main"):
    # Trouver l'élément avec l'attribut id="0"
        item_0 = root.find('.//{http://www.ipc.com/ver10}item[@id="0"]')
    else:
        item_0 = root.find('.//{http://www.ipc.com/ver10}item[@id="1"]')

    # Afficher le contenu de l'élément sans l'espace de nommage
    if item_0 is not None:
        for child in item_0:
            tag_name = child.tag.split('}')[-1]  # Récupérer le nom de la balise sans l'espace de nommage
            print(tag_name, child.text)


def extract_stream_caps(xml_str, stream):
    root = ET.fromstring(xml_str)
    # Find the resolutionCaps element
    if(stream=="main"):
        resolution_caps = root.find('.//{http://www.ipc.com/ver10}item[@id="0"]/{http://www.ipc.com/ver10}resolutionCaps')
    else: 
        resolution_caps = root.find('.//{http://www.ipc.com/ver10}item[@id="1"]/{http://www.ipc.com/ver10}resolutionCaps')

    # Extract values of the item elements within resolutionCaps
    resolutions = [item.text for item in resolution_caps.findall('.//{http://www.ipc.com/ver10}item')]

    # Print the extracted resolutions
    print("Résolutions possibles:")
    for resolution in resolutions:

        print(resolution)



auth = None



def getNbCameras(ip, username, password):
    url = "http://"+ip+"/GetChannelList"
    global auth



    # Création de l'en-tête d'autorisation en utilisant HTTPBasicAuth
    auth = HTTPBasicAuth(username, password)

    # Effectuer la requête GET (ou POST, etc.) avec l'authentification
    response = requests.get(url, auth=auth)



    # Vérifier le statut de la réponse
    if response.status_code == 200:
        # La requête a réussi
        print("Réponse réussie !")
        
        # Vérifier si la réponse contient des données
        if response.text:  
            try:
                # Parser le XML
                root = ET.fromstring(response.text)

                # Trouver l'élément channelIDList
                channel_id_list_element = root.find('.//{http://www.ipc.com/ver10}channelIDList')

                # Vérifier si l'élément a été trouvé
                if channel_id_list_element is not None:
                    # Extraire la valeur de l'attribut count (le nombre 16)
                    count_value = channel_id_list_element.get('count')
                    ###print(count_value)
                    return count_value
                else:
                    return None
            except ET.ParseError as e:
                print(f"Erreur lors du parsing du XML : {e}")
                return None

        else:
            print("La réponse est vide.")
    else:
        # La requête a échoué
        print(f"Échec de la requête avec le code d'état {response.status_code}")
        print(response.text)  # Affiche le contenu de la réponse en cas d'échec




def getCameraActualConfig(ip,username, password, channels, caractere):
    if(caractere =="yes"):
        total_cameras = getNbCameras(ip,username,password)
        if(channels == 'all_main'):
            for camera in range(int(total_cameras)):
                url_actual_config =  "http://"+ip+"/GetVideoStreamConfig/"+str(camera)
                response_actual_config = requests.get(url_actual_config, auth=auth)
                if response_actual_config.status_code == 200:
                    # Vérifier si la réponse contient des données
                    if response_actual_config.text:
                        print('\n============Camera '+str(camera)+'================\n')
                        print("Main Stream :\n")
                        extract_stream_data(response_actual_config.text, "main")
                print('\n==========================================================\n')
        elif(channels == 'all_sub'):
            for camera in range(int(total_cameras)):
                url_actual_config =  "http://"+ip+"/GetVideoStreamConfig/"+str(camera)
                response_actual_config = requests.get(url_actual_config, auth=auth)
                if response_actual_config.status_code == 200:
                    # Vérifier si la réponse contient des données
                    if response_actual_config.text:
                        print('\n============Camera '+str(camera)+'================\n')
                        print("Secondary Stream :\n")
                        extract_stream_data(response_actual_config.text, "sub1")
                print('\n==========================================================\n')
        
        else:
                url_actual_config =  "http://"+ip+"/GetVideoStreamConfig/"+str(channels)
                response_actual_config = requests.get(url_actual_config, auth=auth)
                if response_actual_config.status_code == 200:
                    # Vérifier si la réponse contient des données
                    if response_actual_config.text:
                        print('\n==========================================================\n')
                        print("Main Stream :\n")
                        extract_stream_data(response_actual_config.text, "main")
                        print("Secondary Stream :\n")
                        extract_stream_data(response_actual_config.text, "sub1")
                print('\n==========================================================\n')



def getCameraCapacities(ip, username, password):
    total_cameras = getNbCameras(ip, username, password)
    print('Voici ses capacités : \n')
    url_capacities = "http://"+ip+"/GetStreamCaps/1"


        # Effectuer la requête GET (ou POST, etc.) avec l'authentification
    response_capacities = requests.get(url_capacities, auth=auth)

        # Vérifier le statut de la réponse
    if response_capacities.status_code == 200:
        print("Main Stream :\n")
        extract_stream_caps(response_capacities.text, "main")
        print("Secondary Stream :\n")
        extract_stream_caps(response_capacities.text, "sub1")
    else:
        print('Erreur capacities.')


def traitement_camera(ip, username, password, channels, resolution, fps, bitrate, compression, quality):

    total_cameras = getNbCameras(ip,username,password)
    if not channels.isdigit():
        if(channels.lower()=='main' or channels.lower()=='all_main'):

            xml_data = '''
    <?xml version="1.0" encoding="UTF-8"?>
    <config version="1.0" xmlns="http://www.ipc.com/ver10">
    <streams type="list" count="2">
                    <item id="0">
    '''
        elif(channels.lower()=='sub' or channels.lower()=='all_sub'):
            xml_data = '''
    <?xml version="1.0" encoding="UTF-8"?>
    <config version="1.0" xmlns="http://www.ipc.com/ver10">
    <streams type="list" count="2">
                    <item id="1">
    '''


        if(resolution!=None):
            xml_data += '''<resolution>'''+str(resolution)+'''</resolution>'''

        if(fps!=None):
            xml_data += '''<frameRate type="uint32">'''+str(fps)+'''</frameRate>'''

        if(bitrate!=''):
            xml_data += '''<bitRateType type="bitRateType">'''+str(bitrate)+'''</bitRateType>'''

        if(compression!=None):
            xml_data += '''<encodeType>'''+str(compression)+'''</encodeType>'''

        if(quality!=None):
            xml_data += '''<quality type="quality">'''+str(quality)+'''</quality>'''

        xml_data+= '''
                    </item>
                </streams>

        </config>'''

        for camera in range(int(total_cameras)):
            url_set_sub1 = "http://"+ip+"/SetVideoStreamConfig/"+str(camera)

            response_set_sub1 = requests.post(url_set_sub1, auth=auth,data=xml_data)
        if response_set_sub1.status_code == 200:
            print('Modification réussie pour la caméra \n'+str(camera))
    else:
        xml_data = '''
    <?xml version="1.0" encoding="UTF-8"?>
    <config version="1.0" xmlns="http://www.ipc.com/ver10">
    <streams type="list" count="2">
                    <item id="1">
    '''


        if(resolution!=None):
            xml_data += '''<resolution>'''+str(resolution)+'''</resolution>'''

        if(fps!=None):
            xml_data += '''<frameRate type="uint32">'''+str(fps)+'''</frameRate>'''

        if(bitrate!=''):
            xml_data += '''<bitRateType type="bitRateType">'''+str(bitrate)+'''</bitRateType>'''

        if(compression!=None):
            xml_data += '''<encodeType>'''+str(compression)+'''</encodeType>'''

        if(quality!=None):
            xml_data += '''<quality type="quality">'''+str(quality)+'''</quality>'''

        xml_data+= '''
                    </item>
                </streams>

        </config>'''

        
        url_set_sub1 = "http://"+ip+"/SetVideoStreamConfig/"+str(channels)

        response_set_sub1 = requests.post(url_set_sub1, auth=auth,data=xml_data)
        if response_set_sub1.status_code == 200:
            print('Modification réussie pour la caméra \n'+str(camera))





def get_country_time(country):
    try:
        # Obtenez le fuseau horaire du pays à partir du code de pays
        country_timezone = pytz.country_timezones.get(country.upper())
        if country_timezone:
            # Convertir l'heure UTC actuelle au fuseau horaire du pays
            country_time = datetime.now(pytz.timezone(country_timezone[0]))
            country_time_formatted = country_time.strftime("%Y-%m-%d %H:%M:%S")
            return country_time_formatted

        else:
            return f"Impossible de trouver le fuseau horaire pour le pays avec le code {'GB'}."
    except Exception as e:
        print("Une erreur s'est produite lors de la récupération de l'heure du pays :", e)
        return None

# Get the current time in the local time zone
def setTime(ip, username, password, country):

    auth = HTTPBasicAuth(username, password)
    url_before = "http://"+ip+"/GetDateAndTime"
    response_before = requests.get(url_before, auth=auth)
    print(response_before.text)

    local_now_string = get_country_time(country)
    url_time = "http://"+ip+"/SetDateAndTime"

    xml_data = '''
<config version="1.0" xmlns="http://www.ipc.com/ver10">
        <types>
                <synchronizeType>
                        <enum>manually</enum>
                        <enum>NTP</enum>
                </synchronizeType>
        </types>
        <time>
                <timezoneInfo>
                        <timeZone type="string">CET-1CEST,M3.5.0,M10.5.0/3</timeZone>
                        <daylightSwitch type="boolean">true</daylightSwitch>
                </timezoneInfo>
                <synchronizeInfo>
                        <type type="synchronizeType">manually</type>
                        <ntpServer type="string" maxLen="127">time.windows.com</ntpServer>
                        <currentTime type="string"><![CDATA['''+local_now_string+''']]></currentTime>
                </synchronizeInfo>
        </time>
</config>
'''
    response_time = requests.post(url_time, auth=auth, data= xml_data)
    url_after = "http://"+ip+"/GetDateAndTime"
    response_after = requests.get(url_after, auth=auth)
    print('New configuration:')
    print(response_after.text)







    


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, required=True)
    parser.add_argument("--u", type=str, required=True)
    parser.add_argument("--p", type=str, required=True)
    parser.add_argument("--ch", type=str, required=False)
    parser.add_argument("--r", type=str, required=False)
    parser.add_argument("--f", type=str, required=False)
    parser.add_argument("--b", type=str, required=False)
    parser.add_argument("--c", type=str, required=False)
    parser.add_argument("--q", type=str, required=False)
    parser.add_argument("--country", type=str, required=False)

    args = parser.parse_args()

        ##GET ACTUAL CONFIGURATION
    if args.ip != None and args.u != None and args.p!= None  and args.ch != None and args.r== None and args.f== None and args.b== None and args.c== None and args.q== None and args.country==None:
       getCameraActualConfig(args.ip, args.u, args.p, args.ch, "yes")
       
       ##SET TIME
    if args.ip != None and args.u != None and args.p!= None and args.country!=None:
        setTime(args.ip, args.u, args.p, args.country)


       ##SET CONFIGURATION
    if args.ip != None and args.u != None and args.p!= None and args.ch != None:
        traitement_camera(args.ip, args.u, args.p, args.ch, args.r, args.f, args.b, args.c, args.q)
    
      ##GET CAPACITIES
    if args.ip != None and args.u != None and args.p!= None  and args.ch == None and args.r== None and args.f== None and args.b== None and args.c== None and args.q== None and args.country==None:
       getCameraCapacities(args.ip, args.u, args.p)