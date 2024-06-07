import requests
from requests.auth import HTTPDigestAuth
import re
import argparse
import subprocess
from datetime import datetime
import pytz


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
    command = ['nmap', target_ip, '-p', '1-65535', '--open']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode == 0:
        lines = output.decode('utf-8').split('\n')
        for line in lines:
            if '/tcp' in line:
                port = int(line.split('/')[0])
                open_ports.append(port)
                print(f"Port {port} is open")
    else:
        print(f"Erreur lors de l'exécution de la commande Nmap: {error.decode('utf-8')}")
    return open_ports


def is_http_port(camera_ip, username, password, port):
    urls = [
        f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode[1].ExtraFormat[0]",
        f'http://www.google.com:{port}'
    ]
    for url in urls:
        try:
            r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password), timeout=5)
            r.raise_for_status()
            print(f"test fonctionnel avec port {port}")
            return True
        except requests.exceptions.RequestException:
            continue
    print(f"erreur avec port {port}")
    return False


def numberCam(camera_ip, username, password):
    open_ports = scan_ports(camera_ip)
    potential_http_ports = [port for port in open_ports if is_http_port(camera_ip, username, password, port)]
    port = potential_http_ports[0] if potential_http_ports else None
    if not port:
        print("Aucun port HTTP potentiel trouvé.")
        return [1, None]
    url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Ptz"
    r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password))
    matches = re.findall(r'table\.Ptz\[(\d+)\]', r.text)
    if matches:
        return [int(matches[-1]) + 1, port]
    else:
        print("nombre de camera introuvable")
        return [1, port]


def fetch_camera_config(camera_ip, username, password, channel_id, format_type, cam):
    number = numberCam(camera_ip, username, password)
    port, nbCam = number[1], int(number[0])
    if cam == "yes":
        nbCam = 1

    for x in range(nbCam):
        url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=Encode[{x}].{format_type}[0]"
        r = requests.get(url, stream=True, auth=HTTPDigestAuth(username, password))
        if r.status_code == 200:
            try:
                results = {line.split('=')[0]: line.split('=')[1].strip() for line in r.text.split('\n') if line}
                print(results)
            except:
                continue


def set_camera_parameter(camera_ip, username, password, channel_id, param, value, cam):
    number = numberCam(camera_ip, username, password)
    port, nbCam = number[1], int(number[0])
    if cam == "yes":
        nbCam = 1

    if "all" in channel_id:
        for x in range(nbCam):
            url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&Encode[{x}].{param}={value}"
            r = requests.put(url, stream=True, auth=HTTPDigestAuth(username, password))
            print(f"Setting {param} for camera {x+1}: {r.status_code}")
    else:
        channel_id = int(channel_id) - 1
        url = f"http://{camera_ip}:{port}/cgi-bin/configManager.cgi?action=setConfig&Encode[{channel_id}].{param}={value}"
        r = requests.put(url, stream=True, auth=HTTPDigestAuth(username, password))
        print(f"Setting {param} for camera {channel_id+1}: {r.status_code}")


def get_country_time(pays):
    try:
        country_timezone = pytz.country_timezones.get(pays.upper())
        if country_timezone:
            country_time = datetime.now(pytz.timezone(country_timezone[0]))
            return country_time.strftime("%Y-%m-%d%%20%H:%M:%S")
        else:
            return f"Impossible de trouver le fuseau horaire pour le pays avec le code {pays}."
    except Exception as e:
        print("Une erreur s'est produite lors de la récupération de l'heure du pays :", e)
        return None


def set_time(camera_ip, username, password, country):
    number = numberCam(camera_ip, username, password)
    port = number[1]
    auth = HTTPDigestAuth(username, password)
    local_now_string = get_country_time(country)
    url_time = f"http://{camera_ip}:{port}/cgi-bin/global.cgi?action=setCurrentTime&time={local_now_string}"
    response_time = requests.post(url_time, auth=auth, timeout=5)
    print(f'Time change: {response_time.status_code}')


def reboot_dvr(camera_ip, username, password):
    number = numberCam(camera_ip, username, password)
    port = number[1]
    auth = HTTPDigestAuth(username, password)
    url_reboot = f"http://{camera_ip}:{port}/cgi-bin/magicBox.cgi?action=reboot"
    response_reboot = requests.get(url_reboot, auth=auth, timeout=5)
    print(f'Device reboot: {response_reboot.status_code}')


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
    parser.add_argument("--bc", type=str, required=False)
    parser.add_argument("--country", type=str, required=False)
    parser.add_argument("--reboot", type=str, required=False)
    args = parser.parse_args()

    ip_list = expand_ip_range(args.ip) if "{" in args.ip else [args.ip]

    for ip in ip_list:
        if args.r:
            set_camera_parameter(ip, args.u, args.p, args.ch, "ExtraFormat[0].Video.resolution", args.r, "yes")
        if args.f:
            set_camera_parameter(ip, args.u, args.p, args.ch, "ExtraFormat[0].Video.FPS", args.f, "yes")
        if args.b:
            set_camera_parameter(ip, args.u, args.p, args.ch, "ExtraFormat[0].Video.BitRate", args.b, "yes")
        if args.c:
            set_camera_parameter(ip, args.u, args.p, args.ch, "ExtraFormat[0].Video.Compression", args.c, "yes")
        if args.m:
            set_camera_parameter(ip, args.u, args.p, args.ch, "MotionDetect.Enable", args.m, "yes")
        if args.bc:
            set_camera_parameter(ip, args.u, args.p, args.ch, "ExtraFormat[0].Video.BitRateControl", args.bc, "yes")
        if args.country:
            set_time(ip, args.u, args.p, args.country)
        if args.reboot:
            reboot_dvr(ip, args.u, args.p)
        if not any([args.r, args.f, args.b, args.c, args.m, args.bc, args.country, args.reboot]):
            fetch_camera_config(ip, args.u, args.p, args.ch, "MainFormat" if "main" in args.ch else "ExtraFormat", "yes")
