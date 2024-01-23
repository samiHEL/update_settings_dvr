import requests
import json
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import base64
import hashlib
import re
import argparse
import ipaddress



def test_imagesize():
    base_url = "http://"+'10.151.214.49'+"/axis-cgi/"
    username = 'root'
    password = 'pass'

    api_endpoint = "imagesize.cgi"
    camera_id = "2"
    url = f"{base_url}{api_endpoint}?camera={camera_id}"

    try:
        # Authentification avec les identifiants
        response = requests.get(url, auth=HTTPDigestAuth(username, password))

        # Vérification du code de statut de la réponse
        if response.status_code == 200:
        # Affichage du contenu de la réponse (vous pouvez traiter ces données selon vos >
            print(response.text)
        else:
            print(f"Erreur: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion : {e}")

# Appel de la fonction pour tester /axis-cgi/imagesize.cgi?camera=102
#print(test_imagesize())  



def test_imagesize():
    base_url = "http://"+'10.151.214.51'+"/axis-cgi/"
    username = 'root'
    password = 'pass'
    api_endpoint = "/param.cgi?action=list&group=Properties.Image.Resolution"
    http://myserver/axis-cgi/imagesize.cgi?camera=1

    camera_id = "1"
    url = f"{base_url}{api_endpoint}"
    print(url)
    try:
        # Authentification avec les identifiants
        response = requests.get(url, auth=HTTPDigestAuth(username, password))

        # Vérification du code de statut de la réponse
        if response.status_code == 200:
            print(response.text)
 # Affichage du contenu de la réponse (vous pouvez traiter ces données selon vos >
        else:
            print(f"Erreur: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion : {e}")

def get_nbcameras():
    base_url = "http://"+'10.151.214.49'+"/axis-cgi/"
    username = 'root'
    password = 'pass'

    api_endpoint = "param.cgi"
    url = f"{base_url}{api_endpoint}?action=list&group=Properties.Image.NbrOfViews"

    try:
        # Authentification avec les identifiants
        response = requests.get(url, auth=HTTPDigestAuth(username, password))

        # Vérification du code de statut de la réponse
        if response.status_code == 200:
        # Affichage du contenu de la réponse (vous pouvez traiter ces données selon vos >
            
            print(response.text)
            
        else:
            print(f"Erreur: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion : {e}")


#test_imagesize()



def get_stream_profiles(ip,user,mdp):
    base_url = "http://"+ip+"/axis-cgi/"
    username = user
    password = mdp
    api_endpoint = "streamprofile.cgi"
    url = f"{base_url}{api_endpoint}"

    # Définir les paramètres JSON de la requête
    json_params = {
        "apiVersion": "1.0",
        "context": "",
        "method": "list",
        "params": {
            "streamProfileName": []
        }
    }

    try:
        # Effectuer la requête GET avec les paramètres JSON
        response = requests.post(url, auth=HTTPDigestAuth(username, password), json=json_params)

        # Vérifier le code de statut de la réponse
        if response.status_code == 200:
            # Afficher le contenu de la réponse (vous pouvez traiter ces données selon vos besoins)
            print(response.text)
        else:
            print(f"Erreur: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion : {e}")


def create_stream_profiles(ip,user,mdp,res,fps,codec,method,):
    base_url = "http://"+ip+"/axis-cgi/"
    username = user
    password = mdp
    api_endpoint = "streamprofile.cgi"
    url = f"{base_url}{api_endpoint}"

    # Définir les paramètres JSON de la requête
    json_params = {
        'apiVersion': '1.0',
        'context': '',
        'method': method,
        'params': {
            'streamProfile': [
            {
            'name': 'substream',
            'description': 'test',
            'parameters': 'videocodec='+codec+'&resolution='+res+'&fps='+fps
            }
            ]
        }
    }
    #768x576

    try:
        # Effectuer la requête GET avec les paramètres JSON
        response = requests.post(url, auth=HTTPDigestAuth(username, password), json=json_params)

        # Vérifier le code de statut de la réponse
        if response.status_code == 200:
            # Afficher le contenu de la réponse (vous pouvez traiter ces données selon vos besoins)
            print(response.text)
        else:
            print(f"Erreur: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion : {e}")




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, required=True)
    parser.add_argument("--u", type=str, required=True)
    parser.add_argument("--p", type=str, required=True)
    parser.add_argument("--r", type=str, required=False)
    parser.add_argument("--f", type=int, required=False)
    parser.add_argument("--c", type=str, required=False)
    parser.add_argument("--m", type=str, required=False)
    



    args = parser.parse_args()

    if args.m=="create":
        create_stream_profiles(args.ip, args.u, args.p, args.r, args.f,args.c,"create")
    if args.m=="update":
        create_stream_profiles(args.ip, args.u, args.p, args.r, args.f,args.c,"update")
    if args.r==None:
        get_stream_profiles(args.ip,args.u, args.p)
       



#Test avec axis, mettre streamprofile dans url rtsp VM
#rtsp://root:pass@10.151.214.51:554/axis-media/media.amp?streamprofile=substream&camera=5