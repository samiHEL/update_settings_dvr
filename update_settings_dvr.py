import requests
from requests.auth import HTTPDigestAuth
import re
import argparse
import xml.etree.ElementTree as ET

ns = {'ns': 'http://www.hikvision.com/ver20/XMLSchema'}
ns2 = {'xmlns': 'http://www.std-cgi.com/ver20/XMLSchema'}
ns3 = {'xmlns': 'http://www.std-cgi.org/ver20/XMLSchema'}
ns4 = {'xmlns': 'http://www.isapi.com/ver20/XMLSchema'}



## MODIF RESOLUTION CAM FLUX PRIMAIRE OU SECONDAIRE
def set_resolution(camera_ip, username, password, channel_id, resolution):
    resolution_width = resolution.split("x")[0]
    resolution_height = resolution.split("x")[1]
    if "all"in channel_id:
        number=get_param(camera_ip, username, password)
        for x in range(int(number)):
            print(x+1)
            if channel_id=="all_main":
                channel=x+1
                channel2=str(channel)+"01"
            elif channel_id=="all_sub":
                channel=x+1
                channel2=str(channel)+"02"
           
            # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
            url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel2}'
            #print(url_image_settings)

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")
                return

            # Modifier la résolution

            
            # Modifier le fps
            xml = re.sub(r"<videoResolutionWidth>.*?</videoResolutionWidth>", f"<videoResolutionWidth>{resolution_width}</videoResolutionWidth>", xml)
            xml = re.sub(r"<videoResolutionHeight>.*?</videoResolutionHeight>", f"<videoResolutionHeight>{resolution_height}</videoResolutionHeight>", xml)

            # Effectuer la requête HTTP PUT
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

            # Vérifier si la requête a réussi
            if response.status_code == 200:
                print("Compression pour camera "+str(channel2)+" mise à "+str(resolution)) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")
    else:

        resolution_width = resolution.split("x")[0]
        resolution_height = resolution.split("x")[1]

        # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
        url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel_id}'

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
def set_fps(camera_ip, username, password, channel_id, fps):
    if "all"in channel_id:
        number=get_param(camera_ip, username, password)
        for x in range(int(number)):
            print(x+1)
            if channel_id=="all_main":
                channel=x+1
                channel2=str(channel)+"01"
            elif channel_id=="all_sub":
                channel=x+1
                channel2=str(channel)+"02"
            # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
            url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel2}'
            #print(url_image_settings)

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")
                return

            # Modifier la résolution

            
            # Modifier le fps
            xml = re.sub(r"<maxFrameRate>.*?</maxFrameRate>", f"<maxFrameRate>{fps*100}</maxFrameRate>", xml)

            # Effectuer la requête HTTP PUT
            response = requests.put(url_image_settings, auth=HTTPDigestAuth(username, password), data=xml)

            # Vérifier si la requête a réussi
            if response.status_code == 200:
                print("Compression pour camera "+str(channel2)+" mise à "+str(fps)) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")
    else:


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
            print("Les fps ont été modifiée avec succès.")
            #print(response_put.text)
        else:
            print(f"Erreur : {response_put.status_code} - {response_put.text}")


## MODIF BITREATE CAM ##
def set_bitrate(camera_ip, username, password, channel_id, BitRate):
    if "all"in channel_id:
        number=get_param(camera_ip, username, password)
        for x in range(int(number)):
            print(x+1)
            if channel_id=="all_main":
                channel=x+1
                channel2=str(channel)+"01"
            elif channel_id=="all_sub":
                channel=x+1
                channel2=str(channel)+"02"
            # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
            url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel2}'
            #print(url_image_settings)

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")
                return

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
                print("Compression pour camera "+str(channel2)+" mise à "+str(BitRate)) 
            else:
                print(f"Erreur : {response.status_code} - {response.text}")
    else:
  
        # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
        url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel_id}'

        # Effectuer une requête HTTP GET
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

        # Vérifier si la requête a réussi
        if response_get.status_code == 200:
            xml = response_get.text
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")
            return

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
def set_compression(camera_ip, username, password, channel_id, compression):
    if "all"in channel_id:
        number=get_param(camera_ip, username, password)
        for x in range(int(number)):
            print(x+1)
            if channel_id=="all_main":
                channel=x+1
                channel2=str(channel)+"01"
            elif channel_id=="all_sub":
                channel=x+1
                channel2=str(channel)+"02"
            # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
            url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel2}'
            #print(url_image_settings)

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")
                return

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
            url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel_id}'

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")
                return

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
def get_camera_parameters(camera_ip, username, password, channel_id):
    # Espaces de noms XML
    if "all"in channel_id:
        number=get_param(camera_ip, username, password)
        for x in range(int(number)):
            print(x+1)
            if channel_id=="all_main":
                channel=x+1
                channel2=str(channel)+"01"
            elif channel_id=="all_sub":
                channel=x+1
                channel2=str(channel)+"02"
            url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel2}/'

            try:
                # Effectuer une requête HTTP GET avec une authentification basique
                response = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

                # Vérifier si la requête a réussi (code d'état 200)
                if response.status_code == 200:
                    xml = response.text
                    #print(xml)
                    root = ET.fromstring(xml)

                    if ns is not None:
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
                    elif ns2 is not None:
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
                            vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns2)
                        except:
                            vbr_Upper_Cap =  None
                        try :
                            debit_bin_max = constant_bit_rate.text 
                        except : 
                            debit_bin_max = vbr_Upper_Cap.text    
                        encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns2).text
                    elif ns3 is not None:
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
                            vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns3)
                        except:
                            vbr_Upper_Cap =  None
                        try :
                            debit_bin_max = constant_bit_rate.text 
                        except : 
                            debit_bin_max = vbr_Upper_Cap.text    
                        encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns3).text
                    elif ns4 is not None:
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
                            vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns4)
                        except:
                            vbr_Upper_Cap =  None
                        try :
                            debit_bin_max = constant_bit_rate.text 
                        except : 
                            debit_bin_max = vbr_Upper_Cap.text    
                        encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns4).text

                    print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video)
                    print("-----------")
                else:
                    print(f"Erreur : {response.status_code} - {response.text}")

            except requests.RequestException as e:
                print(f"Erreur de requête : {e}")
    else:
            url_image_settings = f'http://{camera_ip}/ISAPI/Streaming/channels/{channel_id}/'

            try:
                # Effectuer une requête HTTP GET avec une authentification basique
                response = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

                # Vérifier si la requête a réussi (code d'état 200)
                if response.status_code == 200:
                    xml = response.text
                    #print(xml)
                    root = ET.fromstring(xml)

                    if ns is not None:
                        try:
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
                            print("-----------")
                        except:
                            print(xml)
                    elif ns2 is not None:
                        try:
                            id_channel = root.find('.//xmlns:channelName', namespaces=ns2).text
                            width_resolution = root.find('.//xmlns:videoResolutionWidth', namespaces=ns2).text
                            height_resolution = root.find('.//xmlns:videoResolutionHeight', namespaces=ns2).text
                            try :
                                constant_bit_rate = root.find('.//xmlns:constantBitRate', namespaces=ns2)
                            except :
                                constant_bit_rate = None   

                            try : 
                                vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns2)
                            except : 
                                vbr_Upper_Cap =  None
                            type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                            image_par_sec = root.find('.//xmlns:maxFrameRate', namespaces=ns2).text
                            try :
                                debit_bin_max = constant_bit_rate.text 
                            except : 
                                debit_bin_max = vbr_Upper_Cap.text    
                            encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns2).text

                            print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video)
                            print("-----------")
                        except:
                            print(xml)
                    elif ns3 is not None:
                        try:
                            id_channel = root.find('.//xmlns:channelName', namespaces=ns3).text
                            width_resolution = root.find('.//xmlns:videoResolutionWidth', namespaces=ns3).text
                            height_resolution = root.find('.//xmlns:videoResolutionHeight', namespaces=ns3).text
                            try :
                                constant_bit_rate = root.find('.//xmlns:constantBitRate', namespaces=ns3)
                            except :
                                constant_bit_rate = None   

                            try : 
                                vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns3)
                            except : 
                                vbr_Upper_Cap =  None
                            type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                            image_par_sec = root.find('.//xmlns:maxFrameRate', namespaces=ns3).text
                            try :
                                debit_bin_max = constant_bit_rate.text 
                            except : 
                                debit_bin_max = vbr_Upper_Cap.text    
                            encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns3).text

                            print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video)
                            print("-----------")
                        except:
                            print(xml)
                    elif ns4 is not None:
                        try:
                            id_channel = root.find('.//xmlns:channelName', namespaces=ns4).text
                            width_resolution = root.find('.//xmlns:videoResolutionWidth', namespaces=ns4).text
                            height_resolution = root.find('.//xmlns:videoResolutionHeight', namespaces=ns4).text
                            try :
                                constant_bit_rate = root.find('.//xmlns:constantBitRate', namespaces=ns4)
                            except :
                                constant_bit_rate = None   

                            try : 
                                vbr_Upper_Cap =  root.find('.//xmlns:vbrUpperCap', namespaces=ns4)
                            except : 
                                vbr_Upper_Cap =  None
                            type_bande_passante = 'Constant' if constant_bit_rate is not None else 'Variable'
                            image_par_sec = root.find('.//xmlns:maxFrameRate', namespaces=ns4).text
                            try :
                                debit_bin_max = constant_bit_rate.text 
                            except : 
                                debit_bin_max = vbr_Upper_Cap.text    
                            encodage_video = root.find('.//xmlns:videoCodecType', namespaces=ns4).text

                            print_results(id_channel, width_resolution, height_resolution, type_bande_passante, image_par_sec, debit_bin_max, encodage_video)
                            print("-----------")
                        except:
                            print(xml)
                else:
                    print(f"Erreur : {response.status_code} - {response.text}")

            except requests.RequestException as e:
                print(f"Erreur de requête : {e}")

## Recuperer liste parametres flux vidéo secondaire ou primaire ##       
def get_camera_parameters_unique(camera_ip, username, password, ):
    url_image_settings_main = f'http://{camera_ip}/ISAPI/Streaming/channels/101/capabilities'
    url_image_settings_sub = f'http://{camera_ip}/ISAPI/Streaming/channels/102/capabilities'
    tab=[[url_image_settings_main,"primaire"],[url_image_settings_sub,"secondaire"]]
    for t in tab:
        try:
            # Effectuer une requête HTTP GET avec une authentification basique
            response = requests.get(t[0], auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi (code d'état 200)
            if response.status_code == 200:

                xml = response.text
                root = ET.fromstring(xml)
                if ns is not None:

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
                elif ns2 is not None:
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
                elif ns3 is not None:
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
                elif ns4 is not None:
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
            else:
                print(f"Erreur : {response.status_code} - {response.text}")

        except requests.RequestException as e:
            print(f"Erreur de requête : {e}")
def get_param(camera_ip, username, password):
  
    # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
    url_image_settings = f'http://{camera_ip}/ISAPI/System/Video/inputs/channels/'
    #url_image_settings = f'http://{camera_ip}/ISAPI/System/Video/inputs/channels/2/MotionDetection'
    

    # Effectuer une requête HTTP GET
    response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

    # Vérifier si la requête a réussi
    if response_get.status_code == 200:
        xml = response_get.text
        namespace = {'ns': 'http://www.hikvision.com/ver20/XMLSchema'}
        root = ET.fromstring(xml)
        # Utiliser re.search pour extraire la valeur de inputPort pour le dernier VideoInputChannel
        match = re.search(r"<inputPort>(\d+)</inputPort>.*<inputPort>(\d+)</inputPort>", xml, re.DOTALL)
        if match:
            valeur_input_port = match.group(2)
            #print("Valeur de inputPort pour le dernier VideoInputChannel :", valeur_input_port)
            return valeur_input_port
        else:
            print("Balise inputPort non trouvée dans le dernier VideoInputChannel.")
    else:
        print(f"Erreur : {response_get.status_code} - {response_get.text}")
        return

    

def set_motion(camera_ip, username, password, channel_id, motionDetect):
  
    # Exemple d'URL pour accéder aux paramètres d'image (à adapter en fonction de votre caméra)
    if channel_id=="all":
        number=get_param(camera_ip, username, password)
        for x in range(int(number)):
            channel_id=x+1
            url_image_settings = f'http://{camera_ip}/ISAPI/System/Video/inputs/channels/{channel_id}/MotionDetection'

            # Effectuer une requête HTTP GET
            response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

            # Vérifier si la requête a réussi
            if response_get.status_code == 200:
                xml = response_get.text
                # print(xml)
                # print("------------------------------")
            else:
                print(f"Erreur : {response_get.status_code} - {response_get.text}")
                return

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
        url_image_settings = f'http://{camera_ip}/ISAPI/System/Video/inputs/channels/{channel_id}/MotionDetection'

        # Effectuer une requête HTTP GET
        response_get = requests.get(url_image_settings, auth=HTTPDigestAuth(username, password))

        # Vérifier si la requête a réussi
        if response_get.status_code == 200:
            xml = response_get.text
        else:
            print(f"Erreur : {response_get.status_code} - {response_get.text}")
            return

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
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--password", type=str, required=True)
    parser.add_argument("--channel", type=str, required=False)
    parser.add_argument("--resolution", type=str, required=False)
    parser.add_argument("--fps", type=int, required=False)
    parser.add_argument("--bitrate", type=int, required=False)
    parser.add_argument("--compression", type=str, required=False)
    parser.add_argument("--motionDetect", type=str, required=False)

    args = parser.parse_args()
    if args.resolution!=None:
        set_resolution(args.ip, args.username, args.password, args.channel, args.resolution)
    if args.fps!=None:
        set_fps(args.ip, args.username, args.password, args.channel, args.fps)
    if args.bitrate!=None:
        set_bitrate(args.ip, args.username, args.password, args.channel, args.bitrate)
    if args.compression!=None:
        set_compression(args.ip, args.username, args.password, args.channel, args.compression)
    if args.motionDetect!=None:
        set_motion(args.ip, args.username, args.password, args.channel, args.motionDetect)
    if args.channel!=None and args.resolution==None and args.fps==None and args.bitrate==None and args.compression==None and args.motionDetect==None:
        get_camera_parameters(args.ip, args.username, args.password, args.channel)
    if args.channel==None and args.resolution==None and args.fps==None and args.bitrate==None and args.compression==None and args.motionDetect==None:
        get_camera_parameters_unique(args.ip, args.username, args.password)
        #set_motion_all(args.ip, args.username, args.password, "false")
        #get_param(args.ip, args.username, args.password)

## exemple commande Liste parametres flux primaire ou secondaire##
#python3 update_settings_dvr.py --camera_ip 172.24.1.105 --username admin --password Hikvision --channel_id 102

## exemple commande PUT parametres flux primaire ou secondaire##
##python3 update_settings_dvr.py --camera_ip 172.24.1.105 --username admin --password Hikvision --channel_id 102 --resolution 960x576

#Cryptage du flux de caméra HIK
#supp analyse mouvement HIK DAHUA
