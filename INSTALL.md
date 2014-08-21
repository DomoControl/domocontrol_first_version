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
