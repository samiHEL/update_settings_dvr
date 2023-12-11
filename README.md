# update_settings_dvr

### Exemple commande pour une camera : 
python3 update_settings_dvr.py --ip xxx --username admin --password Hikvision --channel 102 --resolution 320x240 

### Exemple commande pour toute les cameras : 

python3 update_settings_dvr.py --ip xxx --username admin --password Hikvision --channel all_sub --resolution 320x240 

### Pour obtenir liste parametres cam dispo lancer :

python3 update_settings_dvr.py --ip xxx --username admin --password Hikvision 

### Pour obtenir Listes cameras sur dvr :

python3 update_settings_dvr.py --ip xxx --username admin --password Hikvision --channel (101,102,all_main, all_sub etc)

## parametre possible :

--ip OBLIGATOIRE 

--username OBLIGATOIRE

--password OBLIGATOIRE

--channel (101,102,201 etc ...) OU (all_main / all_sub)


--resolution (320x240 par ex)

--fps 

--bitrate

--compression (H.264,H.265)

--motionDetect (false ou true)


# update_settings_dvr_Dahua

### Exemple commande : 
python3 update_settings_dvr_dahua.py --ip xxx --username admin --password Dahua123 --channel_id 10 --resolution 704x576 

Id des cameras sont ici sous la forme 1,2,3 etc 
Le code update le flux secondaire par défaut

## parametre possible :

--ip OBLIGATOIRE 

--username OBLIGATOIRE 

--password OBLIGATOIRE 


--channel (1,2,3,4 OU all_main / all_sub etc )

--resolution (704x576 par exemple)

--fps 

--bitrate (1024 par exemple)

--compression (H.264,H.265)

--motionDetect (false ou true)



