from flask import Flask, jsonify, request, render_template, Response
import json
from threading import Thread, Event
import time
import requests
import os
import logging

# Configure logging
log_file = os.path.join('gpio_states', 'app.log')
os.makedirs('gpio_states', exist_ok=True)
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Path to the directory for JSON files
data_directory = 'gpio_states'
os.makedirs(data_directory, exist_ok=True)

# Path for ESP registry file
esp_registry_file = os.path.join(data_directory, 'esp_registry.json')

# Load ESP registry from file
if os.path.exists(esp_registry_file):
    with open(esp_registry_file, 'r') as file:
        esp_registry = json.load(file)
else:
    esp_registry = {}

# Clients connected for real-time updates
clients = []

@app.route('/')
def index():
    logging.info("Accessed home page.")
    return render_template('index.html')

@app.route('/esp-list', methods=['GET'])
def esp_list():
    """Return a list of registered ESP IDs."""
    logging.info("Fetching list of registered ESP devices.")
    return jsonify(list(esp_registry.keys()))

@app.route('/gpio-status/<esp_id>', methods=['GET'])
def get_gpio_status(esp_id):
    """Return the current GPIO status for a specific ESP."""
    logging.info(f'Received GPIO status request for {esp_id}.')
    file_path = os.path.join(data_directory, f'gpio_state_{esp_id}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            gpio_states = json.load(file)
        logging.info(f'Returned GPIO status for {esp_id}: {gpio_states}')
        return jsonify(gpio_states)
    logging.warning(f'ESP {esp_id} not found.')
    return jsonify({'status': 'error', 'message': 'ESP not found'}), 404

@app.route('/gpio-update/<esp_id>', methods=['POST'])
def update_gpio_status(esp_id):
    """Update the GPIO status for a specific ESP."""
    data = request.json
    logging.info(f'Received GPIO update for {esp_id}: {data}')
    file_path = os.path.join(data_directory, f'gpio_state_{esp_id}.json')
    if 'states' in data and len(data['states']) == 6:
        with open(file_path, 'w') as file:
            json.dump(data['states'], file)
        notify_clients(esp_id)  # Notify all connected clients
        notify_esp_device(esp_id, data['states'])  # Notify the specific ESP32 device
        logging.info(f'Updated GPIO status for {esp_id}: {data}')
        return jsonify({'status': 'success'})
    logging.warning(f'Invalid data received for {esp_id}: {data}')
    return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

@app.route('/register-esp', methods=['POST'])
def register_esp():
    """Register an ESP32 device with its IP address."""
    data = request.json
    logging.info(f'Registration request received: {data}')
    if 'esp_id' in data and 'ip_address' in data:
        esp_registry[data['esp_id']] = data['ip_address']
        with open(esp_registry_file, 'w') as file:
            json.dump(esp_registry, file)
        file_path = os.path.join(data_directory, f'gpio_state_{data["esp_id"]}.json')
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                json.dump([0, 0, 0, 0, 0, 0], file)  # Initialize default states
        logging.info(f'ESP {data["esp_id"]} registered successfully with IP {data["ip_address"]}')
        return jsonify({'status': 'success', 'message': 'ESP32 registered successfully'})
    logging.warning(f'Invalid registration data: {data}')
    return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

@app.route('/events/<esp_id>')
def events(esp_id):
    """Server-Sent Events (SSE) endpoint for real-time updates."""
    logging.info(f'Streaming events for {esp_id}.')
    def stream():
        messages = EventStream()
        clients.append((esp_id, messages))
        try:
            for message in messages.listen():
                yield f'data: {message}\n\n'
        except GeneratorExit:
            clients.remove((esp_id, messages))
            logging.info(f'Client {esp_id} disconnected from event stream.')
    return Response(stream(), content_type='text/event-stream')

@app.route('/input-status/<esp_id>', methods=['GET'])
def get_input_status(esp_id):
    """Return the current input GPIO status for a specific ESP."""
    logging.info(f'Received input status request for {esp_id}.')
    file_path = os.path.join(data_directory, f'gpio_state_{esp_id}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            gpio_states = json.load(file)
        input_states = gpio_states[3:]  # Inputs are stored at indices 3, 4, 5
        logging.info(f'Returned input status for {esp_id}: {input_states}')
        return jsonify(input_states)
    logging.warning(f'ESP {esp_id} not found.')
    return jsonify({'status': 'error', 'message': 'ESP not found'}), 404

class EventStream:
    """Manages a stream of events for real-time updates."""
    def __init__(self):
        self.queue = []
        self.event = Event()

    def send(self, message):
        self.queue.append(message)
        self.event.set()

    def listen(self):
        while True:
            self.event.wait()
            while self.queue:
                yield self.queue.pop(0)
            self.event.clear()

# Notify all connected clients of updates
def notify_clients(esp_id):
    logging.info(f'Notifying clients for {esp_id}.')
    for client_esp_id, client in clients:
        if client_esp_id == esp_id:
            file_path = os.path.join(data_directory, f'gpio_state_{esp_id}.json')
            with open(file_path, 'r') as file:
                gpio_states = json.load(file)
            client.send(json.dumps(gpio_states))

def notify_esp_device(esp_id, gpio_states):
    if esp_id in esp_registry:
        ip_address = esp_registry[esp_id]
        try:
            url = f'http://{ip_address}/gpio-update'
            response = requests.post(url, json={'states': gpio_states})
            logging.info(f'Notified {esp_id} at {ip_address}')
        except Exception as e:
            logging.error(f'Error notifying {esp_id}: {e}')

if __name__ == '__main__':
    logging.info("Starting Flask server.")
    app.run(host='0.0.0.0', port=8000, debug=True)
