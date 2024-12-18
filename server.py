from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import os
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import sys
from PIL import Image
import base64
import io
from lib.model_utils import predict_image

# Load environment variables from .env file
load_dotenv()
ENDPOINT = os.getenv('ENDPOINT')

if not ENDPOINT:
    print("ENDPOINT not configured in .env")
    sys.exit()

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
CORS(app)

# Global variables
pattern = r"Temperature:\s*([\d.]+)\s*°C,\s*Humidity:\s*([\d.]+)\s*%"
temperature = 0
humidity = 0
moisture = 0
nitrogen = 0
phosphorus = 0
potassium = 0

# # Initialize serial connection
# try:
#     ser = serial.Serial(ENDPOINT, 115200)
#     time.sleep(2)
# except Exception as e:
#     print(f"Error opening serial port: {e}")
#     sys.exit()

# def read_serial_data():
#     global temperature, humidity
#     while True:
#         if ser.in_waiting > 0:
#             line = ser.readline().decode('utf-8').strip()
#             # print(line)  # Debug print

#             match = re.search(pattern, line)
#             if match:
#                 temperature = float(match.group(1))
#                 humidity = float(match.group(2))

#                 # Emit data to frontend
#                 socketio.emit('change-detected', {'new_temp': temperature, 'new_hum': humidity})
#                 print(f"Temperature: {temperature} °C, Humidity: {humidity} %")  # Debug print

#         time.sleep(1)  # Delay for reading

# Decode base64 to a PIL Image
def base64_to_image(base64_str):
    decoded_image = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(decoded_image))
    return img

# Route for main page
@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/start-threads', methods=['GET'])
# def startthreads():
#     # Start the serial reading thread
#     serial_thread = threading.Thread(target=read_serial_data)
#     serial_thread.start()
#     return jsonify({'status': 'thread started'})

# Flask route for predictions
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400

    try:
        # Decode base64 to image
        img = base64_to_image(data['image'])
        predicted_class = predict_image(img)
     
        predictions = {
            0: 'Potassium defficiency',
            1: 'Healthy',
            2: 'Potassium and Nitrogen defficiency',
            3: 'Nitrogen defficiency'
        }

        descriptions = {
            0: "Potassium deficiency: yellowing along leaf edges, brown spotting. As a remedy, apply potassium-rich fertilizers, avoid excessive watering.",
            1: "Healthy plant with no deficiencies. As a remedy, maintain regular care practices, water and fertilize as needed.",
            2: "Potassium and Nitrogen deficiency: yellowing edges, stunted growth, older leaves yellowing. As a remedy apply a balanced NPK fertilizer to address both deficiencies, and ensure adequate watering.",
            3: "Nitrogen deficiency: yellowing of older leaves, slow growth. As a remedy, use nitrogen-rich fertilizers like compost or urea."
        }

        return jsonify({'predicted_class': predictions[predicted_class], 'desc': descriptions[predicted_class]})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Endpoint for esp to update data    
@app.route('/update-data', methods=['POST'])
def update_data():
    data = request.get_json()

    # Check for required fields in JSON
    required_fields = ['temperature', 'humidity', 'soil_moisture', 'potassium', 'phosphorus', 'nitrogen']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    try:
        # Update global variables
        global temperature, humidity, moisture, potassium, phosphorus, nitrogen
        temperature = data['temperature']
        humidity = data['humidity']
        moisture = data['soil_moisture']
        potassium = data['potassium']
        phosphorus = data['phosphorus']
        nitrogen = data['nitrogen']

        # Emit data to frontend
        socketio.emit('change-detected', {
            'new_temp': temperature,
            'new_hum': humidity,
            'new_moist': moisture,
            'new_potassium': potassium,
            'new_phosphorus': phosphorus,
            'new_nitrogen': nitrogen
        })

        print(f"New data received and emitted, temp: {temperature}, hum: {humidity}, moist: {moisture}, potassium: {potassium}, phosphorus: {phosphorus}, nitrogen: {nitrogen}")

        return jsonify({'status': 'data received'}), 200

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500
    

# Endpoint for sending data to the website once called    
@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    # Fetch data from global variables
    global temperature, humidity, moisture, nitrogen, phosphorus, potassium
    return jsonify({'temperature': temperature, 'humidity': humidity, 'moisture': moisture, 'nitrogen': nitrogen, 'phosphorus': phosphorus, 'potassium': potassium})


# Endpoint to toggle the LED
@app.route('/toggleLED', methods=['GET'])
def toggleLED():
    # Define the LED toggle URL
    url = 'http://192.168.193.217:80/toggle-led'
    
    try:
        # Send request to toggle LED
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad responses (4xx or 5xx)
        
        # Log and return success message
        print(f"Response from toggling LED: {response.status_code}")
        return jsonify({'status': 'LED toggled successfully'}), 200
    except requests.exceptions.RequestException as e:
        # Log and return error message
        print(f"Error toggling LED: {e}")
        return jsonify({'status': 'Error toggling LED', 'error': str(e)}), 500
    
# Start the serial reading in a separate thread
if __name__ == '__main__':
    # Run Flask app
    # serial_thread = threading.Thread(target=read_serial_data)
    # serial_thread.start()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
