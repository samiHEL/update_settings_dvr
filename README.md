# update_settings_dvr
#Exemple commande : python3 update_settings_dvr.py --camera_ip xxx --username admin --password Hikvision --channel_id 102 --resolution_width 320 --resolution_height 240


#parametre possible :

--camera_ip obligatoire 

--username obligatoire 

--password obligatoire 

--channel_id obligatoire 


--resolution_width 

--resolution_height 

--fps 

--bitrate


# update_settings_dvr_Dahua
#Exemple commande : python3 update_settings_dvr_dahua.py --camera_ip xxx --username admin --password Dahua123 --channel_id 10 --resolution 704x576 

Id des cameras sont ici sous la forme 1,2,3 etc 
Le code update le flux secondaire par défaut

#parametre possible :

--camera_ip obligatoire 

--username obligatoire 

--password obligatoire 


--channel_id (1,2,3,4 etc )

--resolution (704x576 par exemple)

--fps 

--bitrate (1024 par exemple)

--compression (H.264,H.265)


