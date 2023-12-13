# update_settings_dvr

### Exemple commande pour une camera : 
python3 update_settings_dvr.py --ip xxx --u admin --p Hikvision --ch 102 --r 320x240 

### Exemple commande pour toute les cameras : 

python3 update_settings_dvr.py --ip xxx --u admin --p Hikvision --ch all_sub --r 320x240 

### Pour obtenir liste parametres cam dispo lancer :

python3 update_settings_dvr.py --ip xxx --u admin --p Hikvision 

### Pour obtenir Listes cameras sur dvr :

python3 update_settings_dvr.py --ip xxx --u admin --p Hikvision --ch (101,102,all_main, all_sub etc)

## parametre possible :

--ip OBLIGATOIRE 

--u OBLIGATOIRE (user)

--p OBLIGATOIRE (password)

--ch (101,102,201 etc ...) OU (all_main / all_sub)


--r (320x240 par ex) (resolution)

--f (fps) 

--b (bitrate)

--c (H.264,H.265) (compression)

--m (false ou true) (motionDetect)


# update_settings_dvr_Dahua

### Exemple commande : 
python3 update_settings_dvr_dahua.py --ip xxx --u admin --p Dahua123 --ch 10 --r 704x576 

Id des cameras sont ici sous la forme 1,2,3 etc 
Le code update le flux secondaire par défaut

## parametre possible :

--ip OBLIGATOIRE 

--u OBLIGATOIRE 

--p OBLIGATOIRE 


--ch (1,2,3,4 OU all_main / all_sub etc )

--r (704x576 par exemple)

--f 

--b (1024 par exemple)

--c (H.264,H.265)

--m (false ou true)



