import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import base64
import hashlib
import re
import argparse
#url = "http://admin:Veesion2023%21@172.24.14.23:80/cgi-bin/snapshot.cgi?channel=1"
#ParamVideo#url = "http://admin:Veesion2023%21@172.24.14.23:80/cgi-bin/devVideoInput.cgi?action=getCaps&channel=1&streamType=2"
##url = "http://admin:Veesion2023%21@172.24.14.23:80/cgi-bin/configManager.cgi?action=getConfig&name=VideoInOptions"
### GetVideoConfigCaps ###
#Liste param video #url = "http://admin:Veesion2023%21@172.24.14.23:80/cgi-bin/encode.cgi?action=getConfigCaps"
### GetVideoEncodeConfig ###
#Bon param video #
# url = "http://admin:Veesion2023%21@172.24.14.23:80/cgi-bin/configManager.cgi?action=getConfig&name=Encode"
#VideoColor#
#url =  "http://admin:Veesion2023%21@172.24.14.23:80/cgi-bin/configManager.cgi?action=getConfig&name=VideoColor"
### SetVideoEncodeConfig ###
##head="table.Encode[15].SnapFormat[1]"


#password=password.encode(encoding="ascii",errors="ignore")
##ExtraFormat[0] Pour flux secondaire##
##MainFormat[0] Pour flux primaire##
## Numero Cam commence à 0 ##
#width="Encode[10].ExtraFormat[0].Video.Width"
#height="Encode[10].ExtraFormat[0].Video.Height"

import subprocess
import time
import importlib

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


def is_http_port(camera_ip, username, password, port,protocol="http"):
    url = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode[1].ExtraFormat[0]"
    url2 = f'{protocol}://www.google.com:{port}' 

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




def print_results(compression_types,resolution_types,fps_types,bitrate_types):
    print('Compression_types : ', compression_types)
    print('Resolution_types: ', resolution_types)
    print('Fps_types : ', fps_types)
    print('Bitrate_types: ', bitrate_types.replace(",","-"))
def print_results_cam(compression_types,resolution_types,fps_types,bitrate_types,channel):
    print('channel : ', channel)
    print('Compression_types : ', compression_types)
    print('Resolution_types: ', resolution_types)
    print('Fps_types : ', fps_types)
    print('Bitrate_types: ', bitrate_types.replace(",","-"))
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import base64
import urllib.request
from urllib.error import HTTPError
from urllib.parse import urlencode
import ssl
import urllib.request
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
def numberCam(camera_ip, username, password,protocol="http"):
        open_ports=scan_ports(camera_ip)
        print(open_ports)
        potential_http_ports = []


        for port in open_ports:
            try:
                if is_http_port(camera_ip, username, password, port,protocol):
                    potential_http_ports.append(port)
                    break  # Sortir de la boucle dès qu'un port HTTP potentiel est trouvé
            except:
                print(f"L'itération pour le port {port} a pris trop de temps (plus de 30 secondes).")
                # Ajoutez ici un code pour gérer le dépassement du temps, si nécessaire

        if potential_http_ports:
            print(f"Le ports HTTP potentiel est: {potential_http_ports[0]}")
        else:
            print("Aucun port HTTP potentiel trouvé.")
        # Encode les informations d'identification
        credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')

        # Construit l'en-tête d'authentification
        headers = {
         "Authorization": f"Basic {credentials}"
        }

        url = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Ptz"
        data = urlencode({}).encode('utf-8')

        try:
           # Effectue la requête avec l'en-tête d'authentification
          request = urllib.request.Request(url, data=data, headers=headers)
          with urllib.request.urlopen(request, context=ssl_context) as response:
            content = response.read().decode('utf-8')
        except HTTPError as e:
            print(f"Error: {e}")
        matches = re.findall(r'table\.Ptz\[(\d+)\]', content)

        # Obtenir le dernier chiffre trouvé
        if matches:
            dernier_chiffre = int(matches[-1])
            return [dernier_chiffre+1,port]
        else:
            print("nombre de camera introuvable")
            return [40,port]




      

            # print("/// Port 80 indisponnible -> Test en cours avec autre port ...")
            # for port in open_ports:
            #     url_test=f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Ptz"
            #     try:
            #         r = requests.get(url_test, stream=True, auth=HTTPDigestAuth(username, password))
            #         t=r.text
            #         matches = re.findall(r'table\.Ptz\[(\d+)\]', t)

            #         # Obtenir le dernier chiffre trouvé
            #         if matches:
            #             dernier_chiffre = int(matches[-1])
            #             return dernier_chiffre+1
            #         else:
            #             print("nombre de camera introuvable")
            #             return 40
            #         break
            #     except:
            #            print("port "+str(port)+" pas compatible en Http")
                       
                      
def getinfoCam(camera_ip, username, password, channel_id,protocol="http"):
    number=numberCam(camera_ip, username, password,protocol)
    port=number[1]

    for x in range(int(number[0])):
            if channel_id=="all_sub":
                # sub = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode["+str(x)+"].ExtraFormat[0]"
                # r = requests.get(sub, stream=True, auth=HTTPDigestAuth(username, password)) 
                # print(r.status_code)
                credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
                # Construit l'en-tête d'authentification
                headers = {
                "Authorization": f"Basic {credentials}"
                }

                url = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Ptz"
                data = urlencode({}).encode('utf-8')

                try:
                    # Effectue la requête avec l'en-tête d'authentification
                    request = urllib.request.Request(url, data=data, headers=headers)
                    with urllib.request.urlopen(request, context=ssl_context) as response:
                        r = response.read().decode('utf-8')
               
                        if response.status == 200:
                                        print("-----")
                                        target_line_compression = next(line for line in r.text.split('\n') if 'table.Encode['+str(x)+'].ExtraFormat[0].Video.Compression' in line)
                                        compression_types = target_line_compression.split('=')[1].strip()
                                        target_line_resolution = next(line for line in r.text.split('\n') if 'table.Encode['+str(x)+'].ExtraFormat[0].Video.resolution' in line)
                                        resolution_types = target_line_resolution.split('=')[1].strip()
                                        target_line_fps = next(line for line in r.text.split('\n') if 'table.Encode['+str(x)+'].ExtraFormat[0].Video.FPS' in line)
                                        fps_types = target_line_fps.split('=')[1].strip()
                                        target_line_bitrate = next(line for line in r.text.split('\n') if 'table.Encode['+str(x)+'].ExtraFormat[0].Video.BitRate' in line)
                                        bitrate_types = target_line_bitrate.split('=')[1].strip()
                                        print_results_cam(compression_types,resolution_types,fps_types,bitrate_types,str(x+1))
                except HTTPError as e:
                        print(f"Error: {e}")
            if channel_id=="all_main":
                sub = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode["+str(x)+"].MainFormat[0]"
                r = requests.get(sub, stream=True, auth=HTTPDigestAuth(username, password)) 
                print(r.status_code)
                if r.status_code == 200:
                                print("-----")
                                target_line_compression = next(line for line in r.text.split('\n') if 'table.Encode['+str(x)+'].MainFormat[0].Video.Compression' in line)
                                compression_types = target_line_compression.split('=')[1].strip()
                                target_line_resolution = next(line for line in r.text.split('\n') if 'table.Encode['+str(x)+'].MainFormat[0].Video.resolution' in line)
                                resolution_types = target_line_resolution.split('=')[1].strip()
                                target_line_fps = next(line for line in r.text.split('\n') if 'table.Encode['+str(x)+'].MainFormat[0].Video.FPS' in line)
                                fps_types = target_line_fps.split('=')[1].strip()
                                target_line_bitrate = next(line for line in r.text.split('\n') if 'table.Encode['+str(x)+'].MainFormat[0].Video.BitRate' in line)
                                bitrate_types = target_line_bitrate.split('=')[1].strip()
                                print_results_cam(compression_types,resolution_types,fps_types,bitrate_types,str(x+1))

def getAllSettings(camera_ip, username, password, protocol="http"):
    number=numberCam(camera_ip, username, password,protocol)
    port=number[1]
    url = f"{protocol}://{camera_ip}:{port}/cgi-bin/encode.cgi?action=getConfigCaps"
    r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password)) 
    print(r.status_code)
    if r.status_code == 200:
                    try:
                        target_line_compression = next(line for line in r.text.split('\n') if 'caps[0].MainFormat[0].Video.CompressionTypes' in line)
                        # Extraire la valeur de ResolutionTypes à partir de la ligne
                        compression_types = target_line_compression.split('=')[1].strip()
                        target_line_resolution = next(line for line in r.text.split('\n') if 'caps[0].MainFormat[0].Video.ResolutionTypes' in line)
                        resolution_types = target_line_resolution.split('=')[1].strip()
                        target_line_fps = next(line for line in r.text.split('\n') if 'caps[0].MainFormat[0].Video.FPSMax' in line)
                        fps_types = target_line_fps.split('=')[1].strip()
                        target_line_bitrate = next(line for line in r.text.split('\n') if 'caps[0].MainFormat[0].Video.BitRateOptions' in line)
                        bitrate_types = target_line_bitrate.split('=')[1].strip()
                        print("Flux primaire")
                        print_results(compression_types,resolution_types,fps_types,bitrate_types)
                        print("-----------")
                        #print(r.text)
                        # Trouver la ligne contenant la valeur de ResolutionTypes
                        target_line_compression = next(line for line in r.text.split('\n') if 'caps[0].ExtraFormat[0].Video.CompressionTypes' in line)
                        # Extraire la valeur de ResolutionTypes à partir de la ligne
                        compression_types = target_line_compression.split('=')[1].strip()
                        target_line_resolution = next(line for line in r.text.split('\n') if 'caps[0].ExtraFormat[0].Video.ResolutionTypes' in line)
                        resolution_types = target_line_resolution.split('=')[1].strip()
                        target_line_fps = next(line for line in r.text.split('\n') if 'caps[0].ExtraFormat[0].Video.FPSMax' in line)
                        fps_types = target_line_fps.split('=')[1].strip()
                        target_line_bitrate = next(line for line in r.text.split('\n') if 'caps[0].ExtraFormat[0].Video.BitRateOptions' in line)
                        bitrate_types = target_line_bitrate.split('=')[1].strip()
                        print("Flux secondaire")
                        print_results(compression_types,resolution_types,fps_types,bitrate_types) 
                        print("-----------")
                    except:
                        target_line_compression = next(line for line in r.text.split('\n') if 'caps.MainFormat[0].Video.CompressionTypes' in line)
                        # Extraire la valeur de ResolutionTypes à partir de la ligne
                        compression_types = target_line_compression.split('=')[1].strip()
                        target_line_resolution = next(line for line in r.text.split('\n') if 'caps.MainFormat[0].Video.ResolutionTypes' in line)
                        resolution_types = target_line_resolution.split('=')[1].strip()
                        target_line_fps = next(line for line in r.text.split('\n') if 'caps.MainFormat[0].Video.FPSMax' in line)
                        fps_types = target_line_fps.split('=')[1].strip()
                        target_line_bitrate = next(line for line in r.text.split('\n') if 'caps.MainFormat[0].Video.BitRateOptions' in line)
                        bitrate_types = target_line_bitrate.split('=')[1].strip()
                        print("Flux primaire")
                        print_results(compression_types,resolution_types,fps_types,bitrate_types)
                        print("-----------")
                        #print(r.text)
                        # Trouver la ligne contenant la valeur de ResolutionTypes
                        target_line_compression = next(line for line in r.text.split('\n') if 'caps.ExtraFormat[0].Video.CompressionTypes' in line)
                        # Extraire la valeur de ResolutionTypes à partir de la ligne
                        compression_types = target_line_compression.split('=')[1].strip()
                        target_line_resolution = next(line for line in r.text.split('\n') if 'caps.ExtraFormat[0].Video.ResolutionTypes' in line)
                        resolution_types = target_line_resolution.split('=')[1].strip()
                        target_line_fps = next(line for line in r.text.split('\n') if 'caps.ExtraFormat[0].Video.FPSMax' in line)
                        fps_types = target_line_fps.split('=')[1].strip()
                        target_line_bitrate = next(line for line in r.text.split('\n') if 'caps.ExtraFormat[0].Video.BitRateOptions' in line)
                        bitrate_types = target_line_bitrate.split('=')[1].strip()
                        print("Flux secondaire")
                        print_results(compression_types,resolution_types,fps_types,bitrate_types) 
                        print("-----------")

def setResolution(camera_ip, username, password, channel_id,resolution,protocol="http"):
    number=numberCam(camera_ip, username, password,protocol)
    port=number[1]
    if "all" in channel_id:
        for x in range(int(number[0])):
            print(x+1)
        
            if channel_id.lower()=="all_sub":   
                resolution_com=f"Encode["+str(x)+"].ExtraFormat[0].Video.resolution"
                url_resolution = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}={resolution}"
                r = requests.put(url_resolution, stream=True, auth=HTTPDigestAuth(username, password)) 
                if r.status_code == 200:
                                print("Resolution pour camera "+str(x+1)+" mise à "+str(resolution))
                elif r.status_code == 400:
                    
                    url_resolution = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}=704x576"
                    r = requests.put(url_resolution, stream=True, auth=HTTPDigestAuth(username, password))
                    print(str(resolution)+" Resolution trop haute DONC resolution mise à 704x576 automatiquement !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
                    
            
            elif channel_id.lower()=="all_main":   
                resolution_com=f"Encode[{x}].MainFormat[0].Video.resolution"
                url_resolution = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}={resolution}"

                print(url_resolution)
                r = requests.put(url_resolution, stream=True, auth=HTTPDigestAuth(username, password)) 
                print(r.status_code)
                if r.status_code == 200:
                                print("Resolution pour camera "+str(x+1)+" mise à "+str(resolution))
                elif r.status_code == 400:
                    print("Pas bon format !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
    else:
            channel_id=int(channel_id)-1
            resolution_com=f"Encode[{channel_id}].ExtraFormat[0].Video.resolution"
            url_resolution = f"{protocol}://{channel_id}:{port}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}={resolution}"

            print(url_resolution)
            r = requests.put(url_resolution, stream=True, auth=HTTPDigestAuth(username, password)) 
            print(r.status_code)
            if r.status_code == 200:
                            print("Resolution pour camera "+str(channel_id)+" mise à "+str(resolution)) 
            elif r.status_code == 400:
                    print("Pas bon format !")
            else : 
                    print(f"Erreur : {r.status_code} - {r.text}")




    
def setFps(camera_ip, username, password, channel_id, fps,protocol="http"):
    number=numberCam(camera_ip, username, password, protocol)
    port=number[1]
    if "all" in channel_id:
        for x in range(int(number[0])):
            print(x+1)
        
            if channel_id.lower()=="all_sub":   
                fps_cam=f"Encode["+str(x)+"].ExtraFormat[0].Video.FPS"

                url_fps = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{fps_cam}={fps}"
                r = requests.put(url_fps, stream=True, auth=HTTPDigestAuth(username, password)) 
                print(r.status_code)
                if r.status_code == 200:
                                print("FPS pour camera "+str(x+1)+" mise à "+str(fps))
                elif r.status_code == 400:
                    print("Pas bon format !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
                    
            
            elif channel_id.lower()=="all_main":   
                fps_cam=f"Encode[{x}].MainFormat[0].Video.FPS"
                url_fps = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{fps_cam}={fps}"

                print(url_fps)
                r = requests.put(url_fps, stream=True, auth=HTTPDigestAuth(username, password)) 
                print(r.status_code)
                if r.status_code == 200:
                                print("FPS pour camera "+str(x+1)+" mise à "+str(fps))
                elif r.status_code == 400:
                    print("Pas bon format !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
    else:
            channel_id=int(channel_id)-1
            fps_cam=f"Encode[{channel_id}].ExtraFormat[0].Video.FPS"
            url_fps = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{fps_cam}={fps}"

            print(url_fps)
            r = requests.put(url_fps, stream=True, auth=HTTPDigestAuth(username, password)) 
            print(r.status_code)
            if r.status_code == 200:
                            print("FPS pour camera "+str(channel_id)+" mise à "+str(fps)) 
            elif r.status_code == 400:
                    print("Pas bon format !")
            else : 
                    print(f"Erreur : {r.status_code} - {r.text}")

def setBitrate(camera_ip, username, password, channel_id, bitrate, protocol="http"):
    number=numberCam(camera_ip, username, password, protocol)
    port=number[1]
    if "all" in channel_id:
        for x in range(int(number[0])):
            print(x+1)
        
            if channel_id.lower()=="all_sub":   
                bitrate_cam=f"Encode[{x}].ExtraFormat[0].Video.BitRate"
                url_bitrate = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{bitrate_cam}={bitrate}"
                r = requests.put(url_bitrate, stream=True, auth=HTTPDigestAuth(username, password)) 
                print(r.status_code)
                if r.status_code == 200:
                                print("BitRate pour camera "+str(x+1)+" mise à "+str(bitrate))
                elif r.status_code == 400:
                    print("Pas bon format !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
                    
            
            elif channel_id.lower()=="all_main":   
                bitrate_cam=f"Encode[{x}].MainFormat[0].Video.BitRate"
                url_bitrate = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{bitrate_cam}={bitrate}"
                r = requests.put(url_bitrate, stream=True, auth=HTTPDigestAuth(username, password)) 
                print(r.status_code)
                if r.status_code == 200:
                                print("BitRate pour camera "+str(x+1)+" mise à "+str(bitrate))
                elif r.status_code == 400:
                    print("Pas bon format !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
    else:
            channel_id=int(channel_id)-1
            bitrate_cam=f"Encode[{channel_id}].ExtraFormat[0].Video.BitRate"
            url_bitrate = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{bitrate_cam}={bitrate}"

            print(url_bitrate)
            r = requests.put(url_bitrate, stream=True, auth=HTTPDigestAuth(username, password)) 
            print(r.status_code)
            if r.status_code == 200:
                            print("BitRate pour camera "+str(channel_id)+" mise à "+str(bitrate)) 
            elif r.status_code == 400:
                    print("Pas bon format !")
            else : 
                    print(f"Erreur : {r.status_code} - {r.text}")

def setCompression(camera_ip, username, password, channel_id, compression,protocol="http"):
    number=numberCam(camera_ip, username, password, protocol)
    port=number[1]
    if "all" in channel_id:
        for x in range(int(number[0])):
            print(x+1)
        
            if channel_id.lower()=="all_sub":   
                compression_cam=f"Encode[{x}].ExtraFormat[0].Video.Compression"
                compression_cam2=f"Encode[{x}].ExtraFormat[0].Video.Profile=Main"
                url_compression = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam}={compression}"
                url_compression_main = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam2}"
                r = requests.put(url_compression, stream=True, auth=HTTPDigestAuth(username, password))
                r2 = requests.put(url_compression_main, stream=True, auth=HTTPDigestAuth(username, password))
                print(r.status_code)
                if r.status_code == 200:
                                print("Compression pour camera "+str(x+1)+" mise à "+str(compression))
                elif r.status_code == 400:
                    print("Pas bon format !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
                    
            
            elif channel_id.lower()=="all_main":   
                compression_cam=f"Encode[{x}].MainFormat[0].Video.Compression"
                compression_cam2=f"Encode[{x}].MainFormat[0].Video.Profile=Main"
                url_compression = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam}={compression}"
                url_compression_main = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam2}"
                r = requests.put(url_compression, stream=True, auth=HTTPDigestAuth(username, password))
                r2 = requests.put(url_compression_main, stream=True, auth=HTTPDigestAuth(username, password))
                print(r.status_code)
                if r.status_code == 200:
                                print("Compression pour camera "+str(x+1)+" mise à "+str(compression))
                elif r.status_code == 400:
                    print("Pas bon format !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
    else:
            channel_id=int(channel_id)-1
            compression_cam=f"Encode[{channel_id}].ExtraFormat[0].Video.Compression"
            compression_cam2=f"Encode[{channel_id}].ExtraFormat[0].Video.Profile=Main"
            url_compression = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam}={compression}"
            url_compression_main = f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam2}"
            r = requests.put(url_compression, stream=True, auth=HTTPDigestAuth(username, password))
            r2 = requests.put(url_compression_main, stream=True, auth=HTTPDigestAuth(username, password))
            print(r.status_code)
            if r.status_code == 200:
                            print("Compression pour camera "+str(channel_id+1)+" mise à "+str(compression))
            elif r.status_code == 400:
                print("Pas bon format !")
            else : 
                print(f"Erreur : {r.status_code} - {r.text}")



def setEncryption(camera_ip, username, password):
    url_encrypt = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.eth2.Encryption=On"
    #url_encrypt = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=getConfig&name=WLan"
    r = requests.put(url_encrypt, stream=True, auth=HTTPDigestAuth(username, password))
    #r = requests.put(url_compression_main, stream=True, auth=HTTPDigestAuth(username, password))
    print(r.status_code)
    if r.status_code == 200:
                    print(r.text) 
def setDetection(camera_ip, username, password,channel_id,motionDetect, protocol="http"):
    number=numberCam(camera_ip, username, password, protocol)
    port=number[1]
    if "all" in channel_id:
        for x in range(int(number[0])):
            print(x+1)
        
            if channel_id.lower()=="all_sub" or channel_id.lower()=="all_main":   

                url_detection=f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&MotionDetect[{x}].Enable={motionDetect.lower()}"
                #print(url_detection)
                r = requests.put(url_detection, stream=True, auth=HTTPDigestAuth(username, password))
                print(r.status_code)
                if r.status_code == 200:
                    print(r.text)
                    print("Detection mouvement pour camera "+str(x+1)+" mise à "+motionDetect.lower()) 
                elif r.status_code == 400:
                    print("Pas bon format !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
                    
    else:
            channel_id=int(channel_id)-1
            channel_str=channel_id+1
            url_detection=f"{protocol}://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&MotionDetect[{channel_id}].Enable={motionDetect.lower()}"
            r = requests.put(url_detection, stream=True, auth=HTTPDigestAuth(username, password))
            print(r.status_code)
            if r.status_code == 200:
                print(r.text)
                print("Detection mouvement pour camera "+str(channel_str)+" mise à "+motionDetect.lower()) 
            elif r.status_code == 400:
                print("Pas bon format !")
            else : 
                print(f"Erreur : {r.status_code} - {r.text}")
def setEncrypt(camera_ip, username, password):
    url_encrypt=f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.wlan0.Enable=true"
    url_encrypt2=f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.wlan0.KeyFlag=true"
    url_encrypt3=f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&WLan.wlan0.Encryption=On"
    url_encrypt4=f"http://{camera_ip}/cgi-bin/configManager.cgi?action=getConfig&name=WLan"
    #print(url_detection)
    r = requests.put(url_encrypt, stream=True, auth=HTTPDigestAuth(username, password))
    r2 = requests.put(url_encrypt2, stream=True, auth=HTTPDigestAuth(username, password))
    r3 = requests.put(url_encrypt3, stream=True, auth=HTTPDigestAuth(username, password))
    r4 = requests.get(url_encrypt4, stream=True, auth=HTTPDigestAuth(username, password))
    print(r4.status_code)
    if r4.status_code == 200:

                    
                    print(r4.text)



#getinfoCam()
#setCompression("172.24.14.23","admin","Veesion2023!",8,"H.264")

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
    parser.add_argument("--ptc", type=str, required=True)

    args = parser.parse_args()
    if args.r!=None:
        setResolution(args.ip, args.u, args.p, args.ch, args.r, args.ptc)
    if args.f!=None:
        setFps(args.ip, args.u, args.p, args.ch, args.f, args.ptc)
    if args.b!=None:
        setBitrate(args.ip, args.u, args.p, args.ch, args.b, args.ptc)
    if args.c!=None:
        setCompression(args.ip, args.u, args.p, args.ch, args.c, args.ptc)
    if args.m!=None:
        setDetection(args.ip, args.u, args.p, args.ch,args.m, args.ptc)  
    if args.ch!=None and args.c==None and args.b==None and args.f==None and args.r==None and args.m==None:
        getinfoCam(args.ip, args.u, args.p,args.ch, args.ptc)
    if args.ch==None and args.c==None and args.b==None and args.f==None and args.r==None and args.m==None:
        getAllSettings(args.ip, args.u, args.p, args.ptc)


