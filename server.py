from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import os
from flask_cors import CORS
from dotenv import load_dotenv
import sys
from PIL import Image
import base64
import io
from model_utils import predict_image

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

        return jsonify({'predicted_class': predictions[predicted_class]})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/update-data', methods=['POST'])
def update_data():
    data = request.get_json()

    if 'temperature' not in data or 'humidity' not in data:
        return jsonify({'error': 'No temperature or humidity provided'}), 400
    
    try:
        global temperature, humidity
        temperature = data['temperature']
        humidity = data['humidity']

        # Emit data to frontend
        socketio.emit('change-detected', {'new_temp': temperature, 'new_hum': humidity})

        print(f"New data received and emitted, temp: {temperature} hum: {humidity}")
        return jsonify({'status': 'data received'}), 200
    
    except Exception as e:
        print(f"Exception occured: {e}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/update-npk', methods=['POST'])
def update_npk_data():
    data = request.get_json()

    if 'Nitrogen' not in data or 'Phosphorus' not in data or 'Potassium' not in data:
        return jsonify({'error': 'Missing values in the json received'}), 400
    
    try:
        global nitrogen, phosphorus, potassium
        nitrogen = data['Nitrogen']
        phosphorus = data['Phosphorus']
        potassium = data['Potassium']

        # Emit data to frontend
        socketio.emit('change-detected', {'nitrogen': nitrogen, 'phosphorus': phosphorus, 'potassium': potassium})

        print(f"New data received and emitted, nitogen: {nitrogen}, phosphorus: {phosphorus}, potassium: {potassium}")
        return jsonify({'status': 'data received'}), 200
    
    except Exception as e:
        print(f"Exception occured: {e}")
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    # Fetch data from global variables
    global temperature, humidity, nitrogen, phosphorus, potassium
    return jsonify({'temperature': temperature, 'humidity': humidity, 'nitrogen': nitrogen, 'phosphorus': phosphorus, 'potassium': potassium})
    
# Start the serial reading in a separate thread
if __name__ == '__main__':
    # Run Flask app
    # serial_thread = threading.Thread(target=read_serial_data)
    # serial_thread.start()
    socketio.run(app, host='0.0.0.0', port=80)
