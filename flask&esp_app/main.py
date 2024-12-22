import network
from machine import Pin
from socket import socket, AF_INET, SOCK_STREAM
import sys

led = Pin(2, Pin.OUT)
led.value(0)  # Ensure LED is off initially

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Set static IP address, subnet mask, and gateway
    ip = '192.168.18.104'         # Set your desired static IP address
    subnet = '255.255.255.0'     # Set your subnet mask
    gateway = '192.168.1.1'      # Set your gateway IP address
    dns = '8.8.8.8'              # Optional: Set DNS server (Google's DNS in this example)
    
    wlan.ifconfig((ip, subnet, gateway, dns))  # Assign static IP configuration
    
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        pass
    
    print('Connected to WiFi')
    print('IP address:', wlan.ifconfig()[0])

def start_server():
    addr = ('', 80)
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(addr)
    s.listen(5)
    print("Server running on port 80")
    
    try:
        while True:
            print("Waiting for client connection...")
            conn, addr = s.accept()
            print(f"Client connected from {addr}")
            request = conn.recv(1024).decode()
            print(f"Request received: {request}")
            
            # Check for LED commands
            if '/led/on' in request:
                print("Turning LED ON")
                led.value(1)
            elif '/led/off' in request:
                print("Turning LED OFF")
                led.value(0)
            
            response = "HTTP/1.1 200 OK\n\nLED Updated!"
            print(f"Sending response: {response}")
            conn.send(response.encode())
            conn.close()
            print("Connection closed")
    except KeyboardInterrupt:
        print("Server stopped.")
        s.close()
        sys.exit()

connect_wifi("Rassi Net3", "Holyshit")
start_server()
