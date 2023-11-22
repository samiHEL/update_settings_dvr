import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import base64
import hashlib
import re
from io import StringIO
from PIL import Image
import argparse


# def basic_auth(username, password):
#     auth_str = f"{username}:{password}"
#     auth_str_b64 = base64.b64encode(auth_str.encode()).decode()
#     return HTTPBasicAuth(username, password)

# def digest_auth(username, password, realm, nonce, uri, method='GET', qop=None, nc=None, cnonce=None):
#     HA1 = hashlib.md5(f"{username}:{realm}:{password}".encode()).hexdigest()
#     HA2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()

#     if qop is None:
#         response = hashlib.md5(f"{HA1}:{nonce}:{HA2}".encode()).hexdigest()
#     else:
#         response = hashlib.md5(f"{HA1}:{nonce}:{nc}:{cnonce}:{qop}:{HA2}".encode()).hexdigest()

#     auth_header = (
#         f'Digest username="{username}", realm="{realm}", nonce="{nonce}", '
#         f'uri="{uri}", response="{response}"'
#     )

#     if qop is not None:
#         auth_header += f', qop={qop}, nc={nc}, cnonce="{cnonce}"'

#     return HTTPDigestAuth(username, password, auth_header)

# ip = '172.24.14.23'
# username = 'admin'
# password = 'Veesion2022!'
# channel_id = '102'

# url = f'http://{ip}/cgi-bin/devVideoInput.cgi?action=getCaps&channel={channel_id}'

# try:
#     # Effectuer une requête HTTP GET avec une authentification basique
#     response = requests.get(url, auth=basic_auth(username, password))

#     # Si la première tentative échoue et que l'authentification par base est demandée,
#     # essayer l'authentification digest
#     if response.status_code == 401 and 'WWW-Authenticate' in response.headers:
#         auth_info = re.findall(r'realm="(.+)", nonce="(.+)"', response.headers['WWW-Authenticate'])
#         if auth_info:
#             realm, nonce = auth_info[0]
#             response = requests.get(url, auth=digest_auth(username, password, realm, nonce))

#     # Vérifier si la requête a réussi (code d'état 200)
#     if response.status_code == 200:
#         # Afficher le contenu de la réponse (qui peut contenir des informations sur l'appareil)
#         print(response.text)
#     else:
#         print(f"Erreur : {response.status_code} - {response.text}")

# except requests.RequestException as e:
#     print(f"Erreur de requête : {e}")


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


def print_results(compression_types,resolution_types,fps_types,bitrate_types):
    print('Compression_types : ', compression_types)
    print('Resolution_types: ', resolution_types)
    print('Fps_types : ', fps_types)
    print('Bitrate_types: ', bitrate_types.replace(",","-"))
    
def getinfoCam():
    url = "http://admin:Veesion2023%21@172.24.14.23:80/cgi-bin/configManager.cgi?action=getConfig&name=Encode"


    r = requests.get(url, stream=True, auth=HTTPDigestAuth('admin', 'Veesion2023!')) 
    print(r.status_code)
    if r.status_code == 200:
                    print(r.text)

def getAllSettings(camera_ip, username, password):
    url = f"http://{camera_ip}/cgi-bin/encode.cgi?action=getConfigCaps"


    r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password)) 
    print(r.status_code)
    if r.status_code == 200:
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
                    print_results(compression_types,resolution_types,fps_types,bitrate_types) 
def setResolution(camera_ip, username, password, channel_id, resolution):
    channel_id=int(channel_id)-1
    #password=password.encode(encoding="ascii",errors="ignore")
    ##ExtraFormat[0] Pour flux secondaire##
    ##MainFormat[0] Pour flux primaire##
    ## Numero Cam commence à 0 ##
    #width="Encode[10].ExtraFormat[0].Video.Width"
    #height="Encode[10].ExtraFormat[0].Video.Height"
    resolution_com=f"Encode[{channel_id}].ExtraFormat[0].Video.resolution"
    url_resolution = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&{resolution_com}={resolution}"

    print(url_resolution)
    r = requests.put(url_resolution, stream=True, auth=HTTPDigestAuth(username, password)) 
    print(r.status_code)
    if r.status_code == 200:
                    print(r.text) 
def setFps(camera_ip, username, password, channel_id, fps):
    channel_id=int(channel_id)-1
    password=password.encode(encoding="ascii",errors="ignore")
    fps_cam=f"Encode[{channel_id}].ExtraFormat[0].Video.FPS"
    url_fps = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&{fps_cam}={fps}"

    print(url_fps)
    r = requests.put(url_fps, stream=True, auth=HTTPDigestAuth(username, password))
    print(r.status_code)
    if r.status_code == 200:
                    print(r.text) 
def setBitrate(camera_ip, username, password, channel_id, bitrate):
    channel_id=int(channel_id)-1
    password=password.encode(encoding="ascii",errors="ignore")
    bitrate_com=f"Encode[{channel_id}].ExtraFormat[0].Video.BitRate"
    url_bitrate = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&{bitrate_com}={bitrate}"

    print(url_bitrate)
    r = requests.put(url_bitrate, stream=True, auth=HTTPDigestAuth(username, password))
    print(r.status_code)
    if r.status_code == 200:
                    print(r.text) 
def setCompression(camera_ip, username, password, channel_id, compression):
    channel_id=int(channel_id)-1
    password=password.encode(encoding="ascii",errors="ignore")
    compression_com=f"Encode[{channel_id}].ExtraFormat[0].Video.Compression"
    compression_main= f"Encode[{channel_id}].ExtraFormat[0].Video.Profile=Main"
    url_compression = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&{compression_com}={compression}"
    url_compression_main = f"http://{camera_ip}/cgi-bin/configManager.cgi?action=setConfig&{compression_main}"

    print(url_compression)
    r = requests.put(url_compression, stream=True, auth=HTTPDigestAuth(username, password))
    r = requests.put(url_compression_main, stream=True, auth=HTTPDigestAuth(username, password))
    print(r.status_code)
    if r.status_code == 200:
                    print(r.text) 


#getinfoCam()

#getAllSettings("172.24.14.23","admin","Veesion2023!")
#setResolution("172.24.14.23","admin","Veesion2023!",8,"704x576")
#setFps("172.24.14.23","admin","Veesion2023!",8, 10)
#setBitrate("172.24.14.23","admin","Veesion2023!",8,1024)
#setCompression("172.24.14.23","admin","Veesion2023!",8,"H.264")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--camera_ip", type=str, required=True)
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--password", type=str, required=True)
    parser.add_argument("--channel_id", type=int, required=False)
    parser.add_argument("--resolution", type=str, required=False)
    parser.add_argument("--fps", type=int, required=False)
    parser.add_argument("--bitrate", type=int, required=False)
    parser.add_argument("--compression", type=int, required=False)
    args = parser.parse_args()
    if args.resolution!=None:
        setResolution(args.camera_ip, args.username, args.password, args.channel_id, args.resolution)
    if args.fps!=None:
        setFps(args.camera_ip, args.username, args.password, args.channel_id, args.fps)
    if args.bitrate!=None:
        setBitrate(args.camera_ip, args.username, args.password, args.channel_id, args.bitrate)
    else:
        getAllSettings(args.camera_ip, args.username, args.password)
