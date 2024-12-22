#!/bin/bash

touch /home/sam/server_started.txt

python3 -m http.server 8000
