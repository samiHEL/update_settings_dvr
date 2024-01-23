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

### Exemple commande pour une camera : 

python3 update_settings_dvr_dahua.py --ip xxx --u admin --p Dahua123 --ch 10 --r 704x576 

### Exemple commande pour toute les cameras (DVR): 

python3 update_settings_dvr_dahua.py --ip xxx --u admin --p Dahua123 --ch all_sub --r 704x576 
python3 update_settings_dvr_dahua.py --ip xxx --u admin --p Dahua123 --ch all_main --r 704x576 


### pour Cam IP : 
mettre separer dernier elements adresse ip par des virgule et ne pas oublier les {}.
python3 update_settings_dvr_dahua.py --ip "192.168.100.{101,104}" --u veesion --p Veesion75 --ch all_sub

### Pour obtenir Listes cameras sur dvr :

python3 update_settings_dvr_dahua.py --ip xxx --u admin --p Dahua123 --ch (all_main, all_sub)

### Pour obtenir liste parametres cam dispo lancer :

python3 update_settings_dvr_dahua.py --ip xxx --u admin --p Dahua123

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

"XXX.XXX.XXX.{XXX,XXX,XXX}" quand cam ip


# Axis

### Exemple commande : 
Ici nous ne modifions pas le substream directement mais créons notre propre streamprofile que nous pourrons ensuite utiliser dans notre url rtsp (sur VM):

python3 axis.py --ip 10.151.214.51 --u root --p pass ( lister les streamprofile deja crées)
python3 axis.py --ip 10.151.214.51 --u root --p pass --r 640x480 --f 5 --c h.264 --m create (Créer son propre streamprofile)
python3 axis.py --ip 10.151.214.51 --u root --p pass --r 768x576 --f 10 --c h.264 --m update (modifier un streamprofile déjà présent)

### Parametres possibles : 

--ip OBLIGATOIRE 

--u OBLIGATOIRE 

--p OBLIGATOIRE 

--r (704x576 par exemple)

--f (fps)

--c (h.264)

--m (update ou create)