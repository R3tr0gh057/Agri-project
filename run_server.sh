#!/bin/bash

# Path to your virtual environment
VENV_PATH="./my_project_env"

# Function to handle Ctrl+C and terminate both processes
cleanup() {
    echo "Terminating server.py and ngrok..."
    # Kill all background jobs
    kill $(jobs -p)
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup SIGINT

# Run server.py with sudo in the virtual environment
echo "Running server.py with sudo in the virtual environment..."
sudo "$VENV_PATH/bin/python" server.py &

# Check if server.py started successfully
if [[ $? -eq 0 ]]; then
    echo "server.py started successfully."
else
    echo "Failed to start server.py."
    exit 1
fi

# Start ngrok as a background process
echo "Starting ngrok tunnel..."
ngrok http --domain=bulldog-promoted-accurately.ngrok-free.app http://192.168.193.55:80 &

# Wait for background processes to complete
wait
