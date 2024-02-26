# update_hik

### Exemple commande pour une camera : 
python3 update_hik.py --ip xxx --u admin --p Hikvision **--ch 102** --r 320x240 

### Exemple commande pour toute les cameras : 

python3 update_hik.py --ip xxx --u admin --p Hikvision **--ch all_sub** --r 320x240 

### Obtenir la liste des parametres dispo sur le dvr  :

python3 update_hik.py --ip xxx --u admin --p Hikvision 

### Obtenir resolution actuelle :

python3 update_hik.py --ip xxx --u admin --p Hikvision **--ch all_main OU all_sub**

## parametres possibles :

--ip OBLIGATOIRE 

--u OBLIGATOIRE (user)

--p OBLIGATOIRE (password)

--ch (101,102,201 etc ...) OU (all_main / all_sub)


--r (320x240 par ex) (resolution)

--f (fps) 

--b (bitrate)

--c (H.264,H.265) (compression)

--m (false ou true) (motionDetect)

--encrypt (true ou false) (encryption)




# update_dahua

### Exemple commande pour une camera : 

python3 update_dahua.py --ip xxx --u admin --p Dahua123 --ch 10 --r 704x576 

### Exemple commande pour toute les cameras (DVR): 

python3 update_dahua.py --ip xxx --u admin --p Dahua123 **--ch all_sub** --r 704x576 

python3 update_dahua.py --ip xxx --u admin --p Dahua123 **--ch all_main** --r 704x576 

### Obtenir liste parametres dispo sur la ou les cameras + info droit d'acces lancer :

python3 update_dahua.py --ip xxx --u admin --p Dahua123


# Cam IP Dahua ou Hik : 

Separer dernier elements adresse ip par des virgule et ne pas oublier les {} 

**exemple :** python3 update_dahua.py **--ip "192.168.100.{101,104}"** --u veesion --p Veesion75 --ch all_sub

### Obtenir liste parametres dispo sur la ou les cameras lancer :

**Pour une cam ip :** python3 update_dahua.py --ip xxx --u admin --p Dahua123

**Pour plusieurs cam ip :** python3 update_dahua.py --ip "xxx.{}" --u admin --p Dahua123

### Obtenir resolution actuel sur plusieurs cam IP :

python3 update_dahua.py --ip xxx --u admin --p Dahua123 **--ch (all_main, all_sub)**

## parametres possibles :

--ip OBLIGATOIRE 

--u OBLIGATOIRE 

--p OBLIGATOIRE 


--ch (1,2,3,4 OU all_main / all_sub etc )

--r (704x576 par exemple)

--f 

--b (1024 par exemple)

--c (H.264,H.265)

--m (false ou true) motion

**RAPPEL =** "XXX.XXX.XXX.{XXX,XXX,XXX}" quand cam ip


# Axis

### Exemple commande : 
Ici nous ne modifions pas le substream directement mais créons notre propre streamprofile que nous pourrons ensuite utiliser dans notre url rtsp (sur VM):

python3 axis.py --ip 10.151.214.51 --u root --p pass ( lister les streamprofiles deja crées)

python3 axis.py --ip 10.151.214.51 --u root --p pass --r 640x480 --f 5 --c h.264 --m create (Créer son propre streamprofile par defaut le streamprofile se nomme "substream")

python3 axis.py --ip 10.151.214.51 --u root --p pass --r 768x576 --f 10 --c h.264 --m update (modifier un streamprofile déjà présent)

### Parametres possibles : 

--ip OBLIGATOIRE 

--u OBLIGATOIRE 

--p OBLIGATOIRE 

--r (704x576 par exemple)

--f (fps)

--c (h.264)

--m (update ou create)



## Ressources documentations APIs
- ** HIK **
  https://www.docdroid.net/wlD2i8v/hikvision-isapi-26-ipmd-service-pdf
- ** DAHUA **
  https://community.jeedom.com/uploads/short-url/tTQJPaNah7gZnU12VGGN9ZHEhOk.pdf
- ** AXIS **

- ** TVT **
  http://kamery.elnika.cz/update/tvt/RTSP_FW3.0_opened_telnet/3535NVR/20151222/TVTAPI1.4.pdf
