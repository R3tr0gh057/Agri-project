from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import serial
import os
import re
import time
import threading
from flask_cors import CORS
from dotenv import load_dotenv
import sys
from PIL import Image
import base64
import io
from model_utils import predict_image

# Load environment variables from .env file
load_dotenv()
COM_PORT = os.getenv('COM_PORT')

if not COM_PORT:
    print("COM_PORT not configured in .env")
    sys.exit()

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
CORS(app)

# Global variables
pattern = r"Temperature:\s*([\d.]+)\s*°C,\s*Humidity:\s*([\d.]+)\s*%"
temperature = 0
humidity = 0

# Initialize serial connection
try:
    ser = serial.Serial(COM_PORT, 115200)
    time.sleep(2)
except Exception as e:
    print(f"Error opening serial port: {e}")
    sys.exit()

def read_serial_data():
    global temperature, humidity
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            # print(line)  # Debug print

            match = re.search(pattern, line)
            if match:
                temperature = float(match.group(1))
                humidity = float(match.group(2))

                # Emit data to frontend
                socketio.emit('change-detected', {'new_temp': temperature, 'new_hum': humidity})
                print(f"Temperature: {temperature} °C, Humidity: {humidity} %")  # Debug print

        time.sleep(1)  # Delay for reading

# Decode base64 to a PIL Image
def base64_to_image(base64_str):
    decoded_image = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(decoded_image))
    return img

# Route for main page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-threads', methods=['GET'])
def startthreads():
    # Start the serial reading thread
    serial_thread = threading.Thread(target=read_serial_data)
    serial_thread.start()
    return jsonify({'status': 'thread started'})

# Flask route for predictions
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400

    try:
        # Decode base64 to image
        img = base64_to_image(data['image'])
        
        # Use imported predict function
        predicted_class = predict_image(img)

        return jsonify({'predicted_class': predicted_class})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Start the serial reading in a separate thread
if __name__ == '__main__':
    # Run Flask app
    serial_thread = threading.Thread(target=read_serial_data)
    serial_thread.start()
    socketio.run(app, host='0.0.0.0', port=80)
