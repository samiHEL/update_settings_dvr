import requests
from requests.auth import HTTPDigestAuth
import json

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
print(test_imagesize())  