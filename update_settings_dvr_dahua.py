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

# def install_python_nmap():
#     try:
#         subprocess.check_call(['pip', 'install', 'python-nmap'])
#         print("python-nmap installé avec succès.")
#     except subprocess.CalledProcessError:
#         print("Erreur lors de l'installation de python-nmap.")

# # Appel de la fonction pour installer python-nmap
# install_python_nmap()
import nmap
import socket

def scan_ports(target_ip):
    nm = nmap.PortScanner()
    nm.scan(target_ip, arguments='-p 1-65535 --open')

    open_ports = []

    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            lport = nm[host][proto].keys()
            for port in lport:
                open_ports.append(port)

    return open_ports

def is_http_port(camera_ip, username, password, port):
    url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode[1].ExtraFormat[0]"

    try:
        r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password))
        r.raise_for_status()
        print("test fonctionnel avec port  "+str(port))
        return True  # La connexion a réussi, donc c'est potentiellement un port HTTP
    except (requests.exceptions.RequestException, socket.error):
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
def numberCam(camera_ip, username, password):
        open_ports=scan_ports(camera_ip)
        print(open_ports)
        potential_http_ports = []
        for port in open_ports:
            if is_http_port(camera_ip, username, password, port):
                potential_http_ports.append(port)
                break  # Sortir de la boucle dès qu'un port HTTP potentiel est trouvé

        #potential_http_ports = [port for port in open_ports if is_http_port(camera_ip, username, password, port)]

        if potential_http_ports:
            print(f"Le ports HTTP potentiel est: {potential_http_ports[0]}")
        else:
            print("Aucun port HTTP potentiel trouvé.")
        port=potential_http_ports[0]
        url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Ptz"

        r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password))
        t=r.text
        matches = re.findall(r'table\.Ptz\[(\d+)\]', t)

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
                       
                      
def getinfoCam(camera_ip, username, password):
    number=numberCam(camera_ip, username, password)
    port=number[1]

    for x in range(int(number[0])):
            sub = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode["+str(x)+"].ExtraFormat[0]"
            r = requests.get(sub, stream=True, auth=HTTPDigestAuth(username, password)) 
            print(r.status_code)
            if r.status_code == 200:
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

def getAllSettings(camera_ip, username, password):
    number=numberCam(camera_ip, username, password)
    port=number[1]
    url = f"http://{camera_ip}:{port}/cgi-bin/encode.cgi?action=getConfigCaps"
    r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password)) 
    print(r.status_code)
    if r.status_code == 200:
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

def setResolution(camera_ip, username, password, channel_id,resolution):
    number=numberCam(camera_ip, username, password)
    port=number[1]
    if "all" in channel_id:
        for x in range(int(number[0])):
            print(x+1)
        
            if channel_id.lower()=="all_sub":   
                resolution_com=f"Encode[{x}].ExtraFormat[0].Video.resolution"
                url_resolution = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}={resolution}"
                r = requests.put(url_resolution, stream=True, auth=HTTPDigestAuth(username, password)) 
                if r.status_code == 200:
                                print("Resolution pour camera "+str(x+1)+" mise à "+str(resolution))
                elif r.status_code == 400:
                    
                    url_resolution = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}=704x576"
                    r = requests.put(url_resolution, stream=True, auth=HTTPDigestAuth(username, password))
                    print(str(resolution)+" Resolution trop haute DONC resolution mise à 704x576 automatiquement !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
                    
            
            elif channel_id.lower()=="all_main":   
                resolution_com=f"Encode[{x}].MainFormat[0].Video.resolution"
                url_resolution = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}={resolution}"

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
            url_resolution = f"http://{channel_id}:{port}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}={resolution}"

            print(url_resolution)
            r = requests.put(url_resolution, stream=True, auth=HTTPDigestAuth(username, password)) 
            print(r.status_code)
            if r.status_code == 200:
                            print("Resolution pour camera "+str(channel_id)+" mise à "+str(resolution)) 
            elif r.status_code == 400:
                    print("Pas bon format !")
            else : 
                    print(f"Erreur : {r.status_code} - {r.text}")

    
def setFps(camera_ip, username, password, channel_id, fps):
    number=numberCam(camera_ip, username, password)
    port=number[1]
    if "all" in channel_id:
        for x in range(int(number[0])):
            print(x+1)
        
            if channel_id.lower()=="all_sub":   
                fps_cam=f"Encode[{x}].ExtraFormat[0].Video.FPS"
                url_fps = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{fps_cam}={fps}"
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
                url_fps = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{fps_cam}={fps}"

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
            fps_cam=f"Encode[{channel_id}].MainFormat[0].Video.FPS"
            url_fps = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{fps_cam}={fps}"

            print(url_fps)
            r = requests.put(url_fps, stream=True, auth=HTTPDigestAuth(username, password)) 
            print(r.status_code)
            if r.status_code == 200:
                            print("FPS pour camera "+str(channel_id)+" mise à "+str(fps)) 
            elif r.status_code == 400:
                    print("Pas bon format !")
            else : 
                    print(f"Erreur : {r.status_code} - {r.text}")

def setBitrate(camera_ip, username, password, channel_id, bitrate):
    number=numberCam(camera_ip, username, password)
    port=number[1]
    if "all" in channel_id:
        for x in range(int(number[0])):
            print(x+1)
        
            if channel_id.lower()=="all_sub":   
                bitrate_cam=f"Encode[{x}].ExtraFormat[0].Video.BitRate"
                url_bitrate = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{bitrate_cam}={bitrate}"
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
                url_bitrate = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{bitrate_cam}={bitrate}"
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
            bitrate_cam=f"Encode[{channel_id}].MainFormat[0].Video.BitRate"
            url_bitrate = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{bitrate_cam}={bitrate}"

            print(url_bitrate)
            r = requests.put(url_bitrate, stream=True, auth=HTTPDigestAuth(username, password)) 
            print(r.status_code)
            if r.status_code == 200:
                            print("BitRate pour camera "+str(channel_id)+" mise à "+str(bitrate)) 
            elif r.status_code == 400:
                    print("Pas bon format !")
            else : 
                    print(f"Erreur : {r.status_code} - {r.text}")

def setCompression(camera_ip, username, password, channel_id, compression):
    number=numberCam(camera_ip, username, password)
    port=number[1]
    if "all" in channel_id:
        for x in range(int(number[0])):
            print(x+1)
        
            if channel_id.lower()=="all_sub":   
                compression_cam=f"Encode[{x}].ExtraFormat[0].Video.Compression"
                compression_cam2=f"Encode[{x}].ExtraFormat[0].Video.Profile=Main"
                url_compression = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam}={compression}"
                url_compression_main = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam2}"
                r = requests.put(url_compression, stream=True, auth=HTTPDigestAuth(username, password))
                r2 = requests.put(url_compression_main, stream=True, auth=HTTPDigestAuth(username, password))
                print(r.status_code)
                if r.status_code == 200:
                                print("BitRate pour camera "+str(x+1)+" mise à "+str(compression))
                elif r.status_code == 400:
                    print("Pas bon format !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
                    
            
            elif channel_id.lower()=="all_main":   
                compression_cam=f"Encode[{x}].MainFormat[0].Video.Compression"
                compression_cam2=f"Encode[{x}].MainFormat[0].Video.Profile=Main"
                url_compression = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam}={compression}"
                url_compression_main = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam2}"
                r = requests.put(url_compression, stream=True, auth=HTTPDigestAuth(username, password))
                r2 = requests.put(url_compression_main, stream=True, auth=HTTPDigestAuth(username, password))
                print(r.status_code)
                if r.status_code == 200:
                                print("BitRate pour camera "+str(x+1)+" mise à "+str(compression))
                elif r.status_code == 400:
                    print("Pas bon format !")
                else : 
                    print(f"Erreur : {r.status_code} - {r.text}")
    else:
            channel_id=int(channel_id)-1
            compression_cam=f"Encode[{channel_id}].MainFormat[0].Video.Compression"
            compression_cam2=f"Encode[{channel_id}].MainFormat[0].Video.Profile=Main"
            url_compression = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam}={compression}"
            url_compression_main = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&{compression_cam2}"
            r = requests.put(url_compression, stream=True, auth=HTTPDigestAuth(username, password))
            r2 = requests.put(url_compression_main, stream=True, auth=HTTPDigestAuth(username, password))
            print(r.status_code)
            if r.status_code == 200:
                            print("BitRate pour camera "+str(channel_id+1)+" mise à "+str(compression))
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
def setDetection(camera_ip, username, password,channel_id,motionDetect):
    channel_id=int(channel_id)-1
    channel_str=channel_id+1
    url_detection=f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&MotionDetect[{channel_id}].Enable={motionDetect.lower()}"
    #print(url_detection)
    r = requests.put(url_detection, stream=True, auth=HTTPDigestAuth(username, password))
    print(r.status_code)
    if r.status_code == 200:
                    print(r.text)
                    print("Detection mouvement pour camera "+str(channel_str)+" mise à "+motionDetect.lower()) 
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
        setResolution(args.ip, args.username, args.password, args.channel, args.resolution)
    if args.fps!=None:
        setFps(args.ip, args.username, args.password, args.channel, args.fps)
    if args.bitrate!=None:
        setBitrate(args.ip, args.username, args.password, args.channel, args.bitrate)
    if args.compression!=None:
        setCompression(args.ip, args.username, args.password, args.channel, args.compression)
    if args.motionDetect!=None:
        setDetection(args.ip, args.username, args.password, args.channel,args.motionDetect)  
    if args.channel!=None and args.compression==None and args.bitrate==None and args.fps==None and args.resolution==None and args.motionDetect==None:
        getinfoCam(args.ip, args.username, args.password)
    if args.channel==None and args.compression==None and args.bitrate==None and args.fps==None and args.resolution==None and args.motionDetect==None:
        getAllSettings(args.ip, args.username, args.password)


