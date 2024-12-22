1- first install ngrok on raspberry pi ( check previous rep : NGROK )

2-  make an autolaunch python script on raspberry called booting.py
    this script must autostart when the raspberry pi boot and this script
    must launch a bach file called startup.sh
3-  startup.sh bach file will launch first flaskapp.py wait a few seconds
    then launch ngrok (ngrok forward the trafic from its static global ip
    to the flask app that redirect it to the local ip of the esp32)
3-  i created here for each step a directory that include all necesary files
    for each step
