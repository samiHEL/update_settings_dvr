import requests
from requests.auth import HTTPDigestAuth
import re
import json
import argparse


def getCaps(ip, username, password):
        # Define the URL, username, and password
    url = 'http://'+ip+'/LAPI/V1.0/Channels/0/Media/Video/Capabilities'
    username = username
    password = password


    # Define headers
    headers = {
        'Content-Type': 'application/json'
    }

    auth = HTTPDigestAuth(username,password)
    # Make the request
    response = requests.get(url, auth=auth, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        response_ = json.loads(response.text)
        # Récupérer les éléments avec l'ID 0 et 1 dans StreamCapabilityList
        stream_capability_list = response_["Response"]["Data"]["StreamCapabilityList"]
        for stream_capability in stream_capability_list:
            if stream_capability["ID"] in [0, 1]:
                stream_type = "main stream" if stream_capability["ID"] == 0 else "second stream"
                print(f"{stream_type}:")
                for resolution_capability in stream_capability["ResolutionCapabilityList"]:
                    print('------------------------')
                    print("Width:", resolution_capability["Width"])
                    print("Height:", resolution_capability["Height"])
                    print("Min Bit Rate:", resolution_capability["MinBitRate"])
                    print("Max Bit Rate:", resolution_capability["MaxBitRate"])
                print("Max Frame Rate:", stream_capability["MaxFrameRate"])
                print("Max MJPEG Frame Rate:", stream_capability["MaxMJPEGFrameRate"])
                print()
        
    else:
        print('Request failed with status code:', response.status_code)



def getData(ip, username, password, channels):

    # Define the URL, username, and password
    url = 'http://'+ip+'/LAPI/V1.0/Channels/0/Media/Video/Streams/DetailInfos'
    username = username
    password = password


    # Define headers
    headers = {
        'Content-Type': 'application/json'
    }

    auth = HTTPDigestAuth(username,password)
    # Make the request
    response = requests.get(url, auth=auth, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        response_data = response.json()
        # Récupérer les éléments dans VideoStreamInfos
        if(channels=='all_main'):
            video_stream_infos = response_data["Response"]["Data"]["VideoStreamInfos"][0]
        else:
            video_stream_infos = response_data["Response"]["Data"]["VideoStreamInfos"][1]

        print("------------------------")
        print("ID:", video_stream_infos["ID"])
        print("Enabled:", video_stream_infos["Enabled"])
        video_encode_info = video_stream_infos["VideoEncodeInfo"]
        print("EncodeFormat:", video_encode_info["EncodeFormat"])
        resolution = video_encode_info["Resolution"]
        print("Resolution:")
        print("Width:", resolution["Width"])
        print("Height:", resolution["Height"])
        print("BitRate:", video_encode_info["BitRate"])
        print("BitRateType:", video_encode_info["BitRateType"])
        print("FrameRate:", video_encode_info["FrameRate"])
        print("GOPType:", video_encode_info["GOPType"])
        print("IFrameInterval:", video_encode_info["IFrameInterval"])
        print("ImageQuality:", video_encode_info["ImageQuality"])
        print("SmoothLevel:", video_encode_info["SmoothLevel"])
        print("SVCMode:", video_encode_info["SVCMode"])
        print("SmartEncodeMode:", video_encode_info["SmartEncodeMode"])
        print()
    else:
        print('Request failed with status code:', response.status_code)


def changeData(ip, username, password, channels, resolution, bitrate, framerate, bitrate_type,compression, quality):
    url = 'http://'+ip+'/LAPI/V1.0/Channels/0/Media/Video/Streams/DetailInfos'
    username = username
    password = password
    json_to_send = {}
    headers = {
        'Content-Type': 'application/json'
    }

    auth = HTTPDigestAuth(username,password)
    response = requests.get(url, auth=auth, headers=headers)

    if response.status_code == 200:
        response_ = json.loads(response.text)
        if(resolution):
            width = resolution.split('x')[0]
            height = resolution.split('x')[1]
        if(bitrate_type):
            if(bitrate_type==0):
                type = 'CBR'
            else:
                type = 'VBR'
        if(compression):
            if(compression=='H.264'):
                encode_format = 1
            else:
                encode_format = 2

        if(channels=='all_main'):  ##flux primaire
            if(resolution):
                response_["Response"]["Data"]["VideoStreamInfos"][0]["VideoEncodeInfo"]["Resolution"]["Width"] = width
                response_["Response"]["Data"]["VideoStreamInfos"][0]["VideoEncodeInfo"]["Resolution"]["Height"] = height 
            if(bitrate):
                response_["Response"]["Data"]["VideoStreamInfos"][0]["VideoEncodeInfo"]["BitRate"] = bitrate
            if(bitrate_type):
                response_["Response"]["Data"]["VideoStreamInfos"][0]["VideoEncodeInfo"]["BitRateType"] = type
            if(framerate):
                response_["Response"]["Data"]["VideoStreamInfos"][0]["VideoEncodeInfo"]["FrameRate"] = framerate
            if(compression):
                response_["Response"]["Data"]["VideoStreamInfos"][0]["VideoEncodeInfo"]["EncodeFormat"] = encode_format
            if(quality):
                response_["Response"]["Data"]["VideoStreamInfos"][0]["VideoEncodeInfo"]["ImageQuality"] = quality

        if(channels=='all_sub'):  ##flux secondaire
            if(resolution):
                response_["Response"]["Data"]["VideoStreamInfos"][1]["VideoEncodeInfo"]["Resolution"]["Width"] = width
                response_["Response"]["Data"]["VideoStreamInfos"][1]["VideoEncodeInfo"]["Resolution"]["Height"] = height 
            if(bitrate):
                response_["Response"]["Data"]["VideoStreamInfos"][1]["VideoEncodeInfo"]["BitRate"] = bitrate
            if(bitrate_type):
                response_["Response"]["Data"]["VideoStreamInfos"][1]["VideoEncodeInfo"]["BitRateType"] = type
            if(framerate):
                response_["Response"]["Data"]["VideoStreamInfos"][1]["VideoEncodeInfo"]["FrameRate"] = framerate
            if(compression):
                response_["Response"]["Data"]["VideoStreamInfos"][1]["VideoEncodeInfo"]["EncodeFormat"] = encode_format
            if(quality):
                response_["Response"]["Data"]["VideoStreamInfos"][1]["VideoEncodeInfo"]["ImageQuality"] = quality



        json_to_send["Num"] = response_["Response"]["Data"]["Num"]
        json_to_send["VideoStreamInfos"] = response_["Response"]["Data"]["VideoStreamInfos"]
        url = 'http://'+ip+'/LAPI/V1.0/Channels/0/Media/Video/Streams/DetailInfos'
        username = username
        password = password
        headers = {
            'Content-Type': 'application/json'
        }

        auth = HTTPDigestAuth(username,password)
        response = requests.put(url, auth=auth,json=json_to_send, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Print the response content
            print('modification réussie !')
        else:
            print('Request failed with status code:', response.status_code)


def reboot_dvr(ip, username, password):

            # Define the URL, username, and password
    url = 'http://'+ip+'/LAPI/V1.0/System/Reboot'
    username = username
    password = password

    auth = HTTPDigestAuth(username,password)
    response = requests.put(url, auth=auth)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the response content
        print('The device was successfully restarted.')
    else:
        print('Error restaring the device.')



def expand_ip_range(ip_range):
    ip_list = []
    match = re.match(r'^(\d+\.\d+\.\d+\.)\{([\d,]+)\}$', ip_range)
    
    if match:
        prefix = match.group(1)
        numbers = match.group(2).split(',')
        
        for num in numbers:
            ip_list.append(prefix + num)
    
    return ip_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, required=True)
    parser.add_argument("--u", type=str, required=True)
    parser.add_argument("--p", type=str, required=True)
    parser.add_argument("--ch", type=str, required=False)
    parser.add_argument("--r", type=str, required=False)
    parser.add_argument("--f", type=str, required=False)
    parser.add_argument("--bc", type=str, required=False)
    parser.add_argument("--b", type=str, required=False)
    parser.add_argument("--c", type=str, required=False)
    parser.add_argument("--q", type=str, required=False)
    parser.add_argument("--reboot", type=str, required=False)


    args = parser.parse_args()

if "{" in args.ip :
    ip_list = expand_ip_range(args.ip)
    for ip in ip_list:   
                ##GET CAPACITIES
        if args.ip != None and args.u != None and args.p!= None  and args.ch == None and args.r== None and args.f== None and args.b== None and args.c== None and args.q == None and args.reboot == None:
            getCaps(ip, args.u, args.p)
                ##SET CONFIGURATION
        if (args.ip != None and args.u != None and args.p!= None  and args.ch != None) and (args.r!= None or args.b!= None or args.f!= None or args.bc!= None or args.q != None or args.c != None):
            changeData(ip, args.u, args.p, args.ch, args.r, args.b, args.f, args.bc, args.c, args.q)
                ##GET ACTUAL CONFIGURATION
        if(args.ip!=None and args.u != None and args.p!= None and args.ch != None and args.reboot == None):
            getData(ip, args.u, args.p, args.ch)
                ##Reboot DVR
        if(args.ip!=None and args.u != None and args.p!= None and args.reboot != None):
            reboot_dvr(ip, args.u, args.p)


else:
            ##GET CAPACITIES
    if args.ip != None and args.u != None and args.p!= None  and args.ch == None and args.r== None and args.f== None and args.b== None and args.c== None and args.q == None and args.reboot == None:
        getCaps(args.ip, args.u, args.p)
            ##SET CONFIGURATION
    if (args.ip != None and args.u != None and args.p!= None  and args.ch != None) and (args.r!= None or args.b!= None or args.f!= None or args.bc!= None or args.q != None or args.c != None):
        changeData(args.ip, args.u, args.p, args.ch, args.r, args.b, args.f, args.bc, args.c, args.q)
            ##GET ACTUAL CONFIGURATION
    if(args.ip!=None and args.u != None and args.p!= None and args.ch != None and args.reboot == None):
        getData(args.ip, args.u, args.p, args.ch)
            ##Reboot DVR
    if(args.ip!=None and args.u != None and args.p!= None and args.reboot != None):
        reboot_dvr(args.ip, args.u, args.p)

        


