# this is a luncher for ngrok and server it start blinking 
# gpio 17 then when it lunch the server it light gpio 27
# to use server and files browsing comment the launching of flaskapp.py
# to use to forward trafic from globally to locally to control esp comment startup2.sh file

import RPi.GPIO as GPIO
import subprocess
import time

# Use Broadcom pin numbering
GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

GPIO.output(17, GPIO.HIGH)
time.sleep(1)
GPIO.output(17, GPIO.LOW)
time.sleep(1)
GPIO.output(17, GPIO.HIGH)
time.sleep(1)
GPIO.output(17, GPIO.LOW)
time.sleep(1)
GPIO.output(17, GPIO.HIGH)
time.sleep(1)
GPIO.output(17, GPIO.LOW)



# Function to launch the .sh file
def launch_sh_file():
    
    # Launch the Flask app to forward to esp32 and redirect output to a log file
    with open("/home/sam/flaskapp.log", "a") as log_file:
        subprocess.Popen(
            ["python3", "/home/sam/flaskapp.py"],
            stdout=log_file,
            stderr=log_file
        )
    time.sleep(5)  # Give the Flask app time to start
    
    # launch the first bash file that start NGROK
    subprocess.Popen(["/bin/bash", "/home/sam/startup1.sh"])
    time.sleep(5)
    
    #launch the second bash file that start the server
    #subprocess.Popen(["/bin/bash", "/home/sam/startup2.sh"])
    #time.sleep(3)
    
    #turn on gpio 27 when all files are launched
    GPIO.output(27, GPIO.HIGH)



time.sleep(3)
launch_sh_file()



