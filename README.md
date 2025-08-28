
---

# Smart Agri Project

A comprehensive IoT-powered agriculture monitoring and plant health prediction system. This project integrates ESP32-based hardware sensors, a Python Flask web server, and a modern web interface to provide real-time environmental data and AI-driven plant disease classification.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Hardware Components](#hardware-components)
- [Software Components](#software-components)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [API Endpoints](#api-endpoints)
- [License](#license)
- [Mobile App Availability](#mobile-app-availability)

---

## Overview
This project enables smart agriculture by:
- Collecting real-time data (temperature, humidity, soil moisture, NPK values) from the field using ESP32 microcontrollers and sensors.
- Sending this data to a Flask-based backend for visualization and further processing.
- Providing a web interface for live monitoring and plant disease prediction using deep learning (ResNet-50).

## Features
- **Real-Time Sensor Data:** View live temperature, humidity, soil moisture, and NPK (Nitrogen, Phosphorus, Potassium) values from the field.
- **AI Plant Disease Detection:** Upload plant images for instant health classification (Healthy, Potassium/Nitrogen deficiencies, etc.) using a ResNet-50 model.
- **Remote Hardware Control:** Toggle field devices (e.g., LEDs/lights) via the web interface.
- **SocketIO Live Updates:** Instant frontend updates when new sensor data arrives.
- **ESP32 Integration:** Ready-to-flash Arduino code for ESP32 boards to connect sensors and communicate with the server.

## Hardware Components
- **ESP32 Boards:** For WiFi connectivity and sensor interfacing.
- **Sensors:**
  - DHT11/DHT22 (Temperature & Humidity)
  - NPK Soil Sensor (for Nitrogen, Phosphorus, Potassium)
- **Relay/LED Modules:** For remote control demonstration.

## Software Components
- **Flask Web Server:** Handles API requests, serves the frontend, and manages SocketIO events.
- **PyTorch/Transformers:** For running the ResNet-50 plant disease classifier.
- **Frontend:** HTML/CSS/JS (with SocketIO) for real-time dashboard and image upload.
- **ESP32 Arduino Code:** For sensor reading and WiFi communication (see `hardware/` folder).

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/R3tr0gh057/Agri-project
cd Agri-project
```

### 2. Install Python Dependencies
You can use the provided script or manually install:
```bash
# Using the script (Linux)
bash install_packages.sh
# Or manually
pip install -r requirements.txt
```

### 3. Flash ESP32 Boards
- Use the code in `hardware/esp-32/`, `hardware/npk-code/`, and `hardware/light-code/` for respective ESP32 modules.
- Install required Arduino libraries (see `hardware/esp-32/lib-requirements.txt`).

### 4. Run the Server
```bash
# Using the helper script (Linux)
bash run_server.sh
# Or manually
python server.py
```

### 5. Access the Web Interface
- Open your browser and go to: [http://localhost:5000](http://localhost:5000)
- For remote access, use the ngrok tunnel provided by `run_server.sh`.

## Usage
- **Live Dashboard:** View real-time sensor data as it updates.
- **Image Prediction:** Upload plant images for instant health/disease classification.
- **Test Prediction Locally:**
  ```bash
  python Test/image.py
  ```
- **Hardware Control:** Use the web interface to toggle LEDs/lights connected to ESP32.

## Directory Structure
```
Agri-project/
├── hardware/
│   ├── esp-32/         # ESP32 main board code & requirements
│   ├── light-code/     # ESP32 code for light/relay control
│   └── npk-code/       # ESP32 code for NPK sensor
├── lib/                # Python utility and model code
├── static/             # Frontend JS and CSS
├── templates/          # HTML templates
├── Test/               # Image prediction test scripts
├── server.py           # Main Flask server
├── requirements.txt    # Python dependencies
├── install_packages.sh # Setup script
├── run_server.sh       # Server + ngrok launcher
└── README.md           # This file
```

## API Endpoints
- `GET /` — Main dashboard page
- `POST /predict` — Accepts base64-encoded plant images, returns class & description
- `POST /update-data` — ESP32 posts sensor data (JSON)
- `GET /fetch-data` — Returns latest sensor data (JSON)
- `GET /toggleLED` — Toggles field LED/relay via ESP32

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Mobile App Availability
A companion mobile app is available and works seamlessly with this system once the server and hardware are set up and running. Contact the project maintainer for access or more details.

---
