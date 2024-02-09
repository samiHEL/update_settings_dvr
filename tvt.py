import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import sys


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
parametre = sys.argv[1]


def getNbCameras():
    url = "http://"+parametre+"/GetChannelList"
    global auth
    username = input("Entrer username : ")
    password = input("Entrer password : ")


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

            print(response.text)  # Afficher le contenu brut de la réponse en cas d'échec du décodage JSON
                        # Parser le XML
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



def choisir_camera():
    nbcam = getNbCameras()
    print("Choisissez la caméra que vous souhaitez modifier (0 pour toutes les caméras, 1-"+str(nbcam)+" pour une caméra spécifique):")
    
    while True:
        try:
            choix = int(input("Votre choix : "))
            if 0 <= choix <= int(nbcam):
                ###print(choix)
                return choix
            else:
                print("Veuillez entrer un nombre entre 0 et"+str(nbcam)+".")
        except ValueError:
            print("Veuillez entrer un nombre valide.")

def getCameraActualConfig(idCam):
    url_actual_config =  "http://"+parametre+"/GetVideoStreamConfig/"+str(idCam)
            # Effectuer la requête GET (ou POST, etc.) avec l'authentification
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
        else:
            print("La réponse est vide.")
    else:
        print('Erreur actual config.')

def getCameraCapacities(idCam):
    print('Voici ses capacités : \n')
    url_capacities = "http://"+parametre+"/GetStreamCaps/"+str(idCam)


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

def traitement_camera(camera, flux,resolution, framerate, bitrate, encodetype, quality ):
    print('Vous avez choisi la caméra '+str(camera)+', voici sa configuration actuelle :')
    getCameraActualConfig(camera)
    getCameraCapacities(camera)


    if(flux.lower()=='main'):

        xml_data = '''
<?xml version="1.0" encoding="UTF-8"?>
<config version="1.0" xmlns="http://www.ipc.com/ver10">
<streams type="list" count="2">
                <item id="0">
'''
    else:
        xml_data = '''
<?xml version="1.0" encoding="UTF-8"?>
<config version="1.0" xmlns="http://www.ipc.com/ver10">
<streams type="list" count="2">
                <item id="1">
'''


    if(resolution!=''):
        xml_data += '''<resolution>'''+str(resolution)+'''</resolution>'''

    if(framerate!=''):
        xml_data += '''<frameRate type="uint32">'''+str(framerate)+'''</frameRate>'''

    if(bitrate!=''):
        xml_data += '''<bitRateType type="bitRateType">'''+str(bitrate)+'''</bitRateType>'''

    if(encodetype!=''):
        xml_data += '''<encodeType>'''+str(encodetype)+'''</encodeType>'''

    if(quality!=''):
        xml_data += '''<quality type="quality">'''+str(quality)+'''</quality>'''

    xml_data+= '''
                </item>
            </streams>

    </config>'''

    url_set_sub1 = "http://"+parametre+"/SetVideoStreamConfig/"+str(camera)

    response_set_sub1 = requests.post(url_set_sub1, auth=auth,data=xml_data)


    if response_set_sub1.status_code == 200:
        print('Modification réussie ! Voici la nouvelle configuration\n')

        getCameraActualConfig(camera)





    
def traitement():
    choix_camera = choisir_camera()
    nbCam = getNbCameras()

    if(choix_camera==0):
        print('Vous avez choisi toutes les caméras !')
        flux = input('Flux (main/sub1)')
        resolution_sub1_input = input('Saisissez la nouvelle résolution : ')
        framerate_sub1_input = input('Saisissez le nouveau framerate : ')
        bitrate_sub1_input = input('Saisissez le nouveau bitrate : ')
        encodetype_sub1_input = input('Saisissez le nouveau encode type : ')
        quality_sub1_input = input('Saisissez la nouvelle qualité : ')
        for camera in range(nbCam):
            traitement_camera(choix_camera,flux,resolution_sub1_input, framerate_sub1_input,bitrate_sub1_input, encodetype_sub1_input, quality_sub1_input)




    else:
        flux = input('Flux (main/sub1)')
        resolution_sub1_input = input('Saisissez la nouvelle résolution : ')
        framerate_sub1_input = input('Saisissez le nouveau framerate : ')
        bitrate_sub1_input = input('Saisissez le nouveau bitrate : ')
        encodetype_sub1_input = input('Saisissez le nouveau encode type : ')
        quality_sub1_input = input('Saisissez la nouvelle qualité : ')
        traitement_camera(choix_camera,flux,resolution_sub1_input, framerate_sub1_input,bitrate_sub1_input, encodetype_sub1_input, quality_sub1_input)