this script listen to the trafic comming from raspberry pi to give the
esp32 a global ip address so it can be controled from everywgere.
first it connect as station mode with a fixed static local ip address
192.168.18.104 then start an open socket webserver port 80 check
request for led on and off. 
check the python flask script (flaskapp.py) that with this script

Below is a detailed explanation of each line in your MicroPython script:

import network
from machine import Pin
from socket import socket, AF_INET, SOCK_STREAM
import sys

import network:
This module provides access to Wi-Fi functionality on the ESP32 (e.g., connecting to Wi-Fi, creating an access point).

from machine import Pin:
Imports the Pin class from the machine module, used to control GPIO pins on the ESP32 (e.g., to turn an LED on or off).

from socket import socket, AF_INET, SOCK_STREAM:
Imports classes and constants for creating and managing sockets (network communication endpoints).

AF_INET: Indicates IPv4.
SOCK_STREAM: Specifies the TCP protocol.

import sys:
Provides system-specific functions and parameters, such as exiting the script.

led = Pin(2, Pin.OUT)
led.value(0)             # Ensure LED is off initially
led = Pin(2, Pin.OUT):   Configures GPIO2 as an output pin to control the onboard LED.
led.value(0):            Sets the LED to OFF (logic level 0).

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

Defines a function to connect the ESP32 to a Wi-Fi network.
Creates a WLAN (Wi-Fi) object in station mode (STA_IF), allowing the ESP32 to connect to a router.
wlan.active(True):   Activates the Wi-Fi interface.
    ip = '192.168.18.104'         # Set your desired static IP address
    subnet = '255.255.255.0'     # Set your subnet mask
    gateway = '192.168.1.1'      # Set your gateway IP address
    dns = '8.8.8.8'              # Optional: Set DNS server (Google's DNS in this example)
    
    wlan.ifconfig((ip, subnet, gateway, dns))  # Assign static IP configuration
Static IP Configuration:
ip: The ESP32’s IP address on the network.
subnet: Subnet mask determines the size of the local network.
gateway: The router’s IP address.
dns: The DNS server (optional, used for resolving domain names).
wlan.ifconfig((ip, subnet, gateway, dns)): Assigns these network settings to the ESP32.
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        pass
wlan.connect(ssid, password): Initiates a connection to the Wi-Fi network using the provided SSID and password.
while not wlan.isconnected(): pass: Waits until the ESP32 successfully connects to the Wi-Fi network.
    print('Connected to WiFi')
    print('IP address:', wlan.ifconfig()[0])

def start_server():
    addr = ('', 80)
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(addr)
    s.listen(5)
    

Defines a function to start a simple HTTP server.
addr = ('', 80):
Sets up the server address. An empty string '' binds to all available network interfaces, and 80 is the HTTP port.

s = socket(AF_INET, SOCK_STREAM):   Creates a new TCP socket.
s.bind(addr):    Binds the socket to the specified address and port.
s.listen(5):     Puts the socket into listening mode, allowing it to accept up to 5 queued connections.
print("Server running on port 80")
    
    try:
        while True:
            print("Waiting for client connection...")
            conn, addr = s.accept()
            
Server Loop:
print: Outputs the server status.
s.accept(): Waits for and accepts an incoming client connection, returning a new socket conn and the client’s address addr.
            print(f"Client connected from {addr}")
            request = conn.recv(1024).decode()
            print(f"Request received: {request}")
Request Handling:
Logs the client’s address and the request data received.
conn.recv(1024): Receives up to 1024 bytes of data from the client.
.decode(): Converts the received bytes into a string.
            if '/led/on' in request:
                print("Turning LED ON")
                led.value(1)
            elif '/led/off' in request:
                print("Turning LED OFF")
                led.value(0)
Command Parsing:
Checks if the request contains /led/on or /led/off and updates the LED state accordingly.
            response = "HTTP/1.1 200 OK\n\nLED Updated!"
            print(f"Sending response: {response}")
            conn.send(response.encode())
            conn.close()
Response:
Prepares and sends an HTTP response indicating the LED state was updated.
conn.close(): Closes the client connection.
    except KeyboardInterrupt:
        print("Server stopped.")
        s.close()
        sys.exit()
Error Handling:
Allows the server to stop gracefully if interrupted (e.g., via Ctrl+C).
connect_wifi("Rassi Net3", "Holyshit")
start_server()
connect_wifi("Rassi Net3", "Holyshit"):
Connects the ESP32 to the specified Wi-Fi network.
start_server():
Starts the HTTP server to handle client requests.