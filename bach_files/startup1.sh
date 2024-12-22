#!/bin/bash

# Create a marker file to indicate the script ran
touch /home/sam/ngrok_started.txt

# Ensure the correct PATH for ngrok
export PATH=$PATH:/usr/local/bin

# Kill any existing ngrok or Python HTTP server processes
pkill ngrok
pkill -f 'python3 -m http.server'

# Start ngrok with the specified URL
/usr/local/bin/ngrok http 8000 --url terrier-patient-********.ngrok-free.app
