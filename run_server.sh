#!/bin/bash

# Path to your virtual environment
VENV_PATH="./my_project_env"

# Activate the virtual environment by specifying the Python interpreter directly
echo "Running server.py with sudo in the virtual environment..."

# Run server.py with the virtual environment's Python interpreter and sudo
sudo "$VENV_PATH/bin/python" server.py
