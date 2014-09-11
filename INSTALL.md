=== APPUNTI ===
*** Installare RASPBERRY PI ***
- Prelevare l'immagine RASPBIAN da http://downloads.raspberrypi.org/raspbian_latest
- Scomprimere l'immagine scaricata
- copiare l'immagine nella SDCARD: dd bs=4M if=/home/luca/Scaricati/2014-09-25-wheezy-raspbian.img of=/dev/sde1
- con GPARTED estendere lo spazio della seconda partizione
- collegarsi in SSH: ssh pi@192.168.1.248   password: raspberry
- cambiare password: passwd pi
- abilitare password di root: sudo root  - passwd root
- modificare .bashrc dell'utente root e pi e abilitare la visione a colori e gli alias

=== INDIRIZZO IP STATICO ===
- editare il file /etc/network/interfaces
- anziché "iface eth0 inetdhcp" cambiare in "iface eth0 inet static"
- aggiungere le righe:
	address 192.168.1.248 <<==Indirizzo che si desidera
	gateway 192.168.1.1
	netmask 255.255.255.0

*** Installare Webiopi ***
- prelevare webiopi dal sito http://sourceforge.net/projects/webiopi/files/ : wget http://sourceforge.net/projects/webiopi/files/
- tar xvzf file_prelevato
- cd WebIOPi-0.7.0/  e ./setup.sh
- spostarsi nella home: cd - pi
- clonare il repository domocontrol: git clone https://github.com/DomoControl/domocontrol
- nella directory domocontrol ci saranno tutti i files del progetto

*** Far partire webiopi al boot ***
 update-rc.d webiopi defaults
=== FINE ===


Installare DomoControl
----------------------

- DomoControl funziona con Webiopi: per tutti i dettagli vedere https://code.google.com/p/webiopi/wiki/INSTALL
- DomoControl richiede inoltre: python e sqlite
- Collegarsi in ssh al raspberry: => ssh pi@indirizzo_ip_raspberry
- Prelevare il file da questo indirizzo: http://sourceforge.net/projects/webiopi/files/ => wget http://sourceforge.net/projects/webiopi/files/latest/download?source=files webiopi.tar.gz
- Scomprimere il file scaricato => tar xvzf webiopi.tar.gz
- Entrare nella direcory: cd WebIOPi-0.7.0
- Installare webiopi => sudo ./setup.sh
- Editare il file /etc/webiopi/config => sudo nano /etc/webiopi/config e cambiare nella sezione

[SCRIPTS] 
myscript = /home/pi/domocontrol/python/script.py

[HTTP] 
enabled = true port = 8080 doc-root = /home/pi/domocontrol/html/

- Salvare il file con ctrl+X + S

- Prelevare i files del progetto DomoControl da https://github.com/lucasub/domocontrol con GIT => git clone git: git clone git://github.com/lucasub/domocontrol.git
- Avviare webiopi: sudo /etc/init.d/webiopi restart
- Tramite browser collegarsi a indirizzo_raspberry:8080


Per segnalare errori, modifiche, soluzioni, consigli -> https://github.com/lucasub/domocontrol/issues/new
Grazie
------
