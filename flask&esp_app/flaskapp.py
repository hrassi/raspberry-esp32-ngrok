from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace this with the local IP address of your ESP32
ESP32_IP = '192.168.18.104'

@app.route('/')
def home():
    return "Flask is running and ready to control the ESP32!"

@app.route('/control/led/<action>', methods=['GET'])
def control_led(action):
    if action in ['on', 'off']:
        try:
            # Send the request to the ESP32 to control the LED
            esp_response = requests.get(f'http://{ESP32_IP}/led/{action}')
            
            # Return the ESP32's response to the client
            return jsonify({
                "message": f"LED turned {action} successfully",
                "esp_response": esp_response.text
            }), esp_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Failed to connect to ESP32", "details": str(e)}), 500
    else:
        return jsonify({"error": "Invalid action. Use 'on' or 'off'"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
