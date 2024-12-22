to make the python file booting.py placed in the directory :    /home/sam/startup  run automatically when starting the raspberry  


1- type crontab -e
it will open a crontab file something like : File: /tmp/crontab.y62Acx/crontab .
add at the end of this file this line : 

@reboot /usr/bin/python3 /home/sam/startup/booting.py >> /home/sam/startup/booting.log 2>&1


then control+o and enter to save then control+x to exit

the log.txt file will be created on the first reboot

now we have to create the booting.py script and put it 
in the exact location that the crontab file point to.
(create startup folder and put inside booting.py)

