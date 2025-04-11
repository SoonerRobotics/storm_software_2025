#!/bin/bash

# Navigate to project directory
echo "[INFO] Changing directory to /home/scr/storm_software_2025/operator/"
cd /home/scr/storm_software_2025/operator/ || {
    echo "[ERROR] Failed to change directory. Exiting."
    exit 1
}

# Activate virtual environment
echo "[INFO] Activating Python virtual environment..."
source venv/bin/activate || {
    echo "[ERROR] Failed to activate virtual environment. Exiting."
    exit 1
}

# Navigate to tests directory
echo "[INFO] Changing directory to 'tests/'..."
cd tests || {
    echo "[ERROR] Failed to enter 'tests' directory. Exiting."
    exit 1
}

# Run the Python script
echo "[INFO] Running manual.py..."
python manual.py

# End of script
echo "[INFO] Script finished at $(date)"
