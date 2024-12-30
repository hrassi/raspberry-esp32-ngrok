import network
from machine import Pin
import socket
import ujson
import time
import urequests


led=Pin(2,Pin.OUT)
led.off()

# Wi-Fi credentials
SSID = 'Rassi Net3'
PASSWORD = '*******'

# Flask server details
FLASK_SERVER = 'http://192.168.18.77:8000'  # Replace with Flask server IP
ESP_ID = 'esp1'  # Unique identifier for this ESP32

# GPIO Setup
output_pins = [Pin(25, Pin.OUT), Pin(26, Pin.OUT), Pin(27, Pin.OUT)]
input_pins = [Pin(32, Pin.IN), Pin(34, Pin.IN), Pin(35, Pin.IN)]

# Input state change queue
input_change_queue = []

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    print("Connecting to Wi-Fi...")
    time.sleep(1)

print('Connected to Wi-Fi, IP:', wlan.ifconfig()[0])
led.on()
time.sleep(3)
led.off()

# Register ESP32 with Flask server
def register_with_flask():
    """Register ESP32 with Flask server."""
    url = f'{FLASK_SERVER}/register-esp'
    data = {'esp_id': ESP_ID, 'ip_address': wlan.ifconfig()[0]}
    try:
        response = urequests.post(url, json=data)
        print('ESP Registered:', response.text)
        response.close()
        for z in range(0,20):
            led.on()
            time.sleep(.1)
            led.off()
            time.sleep(.1)
    except Exception as e:
        print('Failed to register ESP with Flask:', e)

# Register ESP32 with Flask server after connecting to Wi-Fi
register_with_flask()

# Function to fetch initial GPIO states from Flask server
def fetch_initial_gpio_states():
    """Fetch initial GPIO states from Flask server and set GPIO outputs."""
    url = f'{FLASK_SERVER}/gpio-status/{ESP_ID}'
    try:
        response = urequests.get(url)
        states = ujson.loads(response.text)
        for i in range(3):
            output_pins[i].value(states[i])  # Set output pins based on server state
        print('Initialized GPIO states:', states)
        response.close()
    except Exception as e:
        print('Failed to fetch initial GPIO states:', e)

# Fetch initial GPIO states
fetch_initial_gpio_states()

# Function to send input states
def send_input_states():
    """Send input GPIO states to the Flask server."""
    # Fetch current output states to avoid overwriting outputs
    output_states = [pin.value() for pin in output_pins]
    input_states = [pin.value() for pin in input_pins]

    url = f'{FLASK_SERVER}/gpio-update/{ESP_ID}'
    data = {'states': output_states + input_states}  # Outputs + Inputs

    try:
        response = urequests.post(url, json=data)
        print('Input states sent:', response.text)
        response.close()
    except Exception as e:
        print('Failed to send input states:', e)

# Interrupt handler for input GPIOs
def input_changed(pin):
    """Handle input GPIO changes by adding to the queue."""
    input_change_queue.append(1)  # Append any signal to the queue
    print(f"Input changed on pin {pin}: {pin.value()}")

# Attach interrupts to input pins
for pin in input_pins:
    pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=input_changed)

# Timer-based input processing loop
import _thread

def check_input_queue():
    """Check and process input state updates from the queue."""
    if input_change_queue:
        input_change_queue.pop(0)  # Remove the item from the queue
        send_input_states()  # Send the updated input states to Flask

def input_processing_loop():
    while True:
        check_input_queue()
        time.sleep(0.1)  # Check the queue every 100ms

_thread.start_new_thread(input_processing_loop, ())

# HTTP Server for Flask updates
def start_http_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print('Listening on', addr)
    led.on()

    while True:
        # Handle HTTP requests
        conn, addr = s.accept()
        print('Client connected from', addr)
        request = conn.recv(1024)
        request = request.decode('utf-8')
        print('Request:', request)

        # Handle POST /gpio-update
        if 'POST /gpio-update' in request:
            try:
                # Extract JSON data from the request
                if '\r\n\r\n' in request:
                    body = request.split('\r\n\r\n')[1]
                else:
                    body = ''
                print(f"Raw Body: {body}")  # Debugging received body

                # Ensure the body is not empty
                if not body.strip():
                    print('Empty Body Received! Checking Flask JSON file...')
                    fetch_initial_gpio_states()  # Fetch and update GPIO outputs
                    response = 'HTTP/1.1 400 Bad Request\r\n\r\n{"error": "Empty body"}'
                else:
                    # Parse the JSON
                    data = ujson.loads(body)
                    states = data.get('states', [])
                    if len(states) == 6:
                        for i in range(3):
                            output_pins[i].value(states[i])
                        print('Updated GPIO states:', states)
                        response = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"status": "success"}'
                    else:
                        response = 'HTTP/1.1 400 Bad Request\r\n\r\n'
            except ValueError as e:
                print('JSON Parsing Error:', e)
                response = 'HTTP/1.1 400 Bad Request\r\n\r\n{"error": "Invalid JSON"}'
            except Exception as e:
                print('Error processing update:', e)
                response = 'HTTP/1.1 500 Internal Server Error\r\n\r\n'
        else:
            response = 'HTTP/1.1 404 Not Found\r\n\r\n'

        conn.send(response)
        conn.close()

# Start the HTTP server
start_http_server()
