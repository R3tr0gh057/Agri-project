#!/bin/bash

# Update package lists
sudo apt update

# Install required system packages
echo "Installing Flask (system-wide)..."
sudo apt install -y python3-flask python3-venv

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv my_project_env

# Activate the virtual environment
source my_project_env/bin/activate

# Install other Python packages within the virtual environment
echo "Installing Python packages with pip..."
pip install pyserial flask-socketio flask-cors python-dotenv gevent torch torchvision huggingface_hub pillow transformers

# Inform the user
echo "All packages installed successfully in the virtual environment 'my_project_env'!"

# Reminder to keep the environment active or how to activate it later
echo "To activate the virtual environment later, use: source my_project_env/bin/activate"
