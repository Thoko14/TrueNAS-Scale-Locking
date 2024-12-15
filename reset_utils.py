import os
import json

DEFAULT_CONFIG = {
    "host": "",
    "username": "",
    "password": "",
    "pool": "",
    "datasets": []
}

CONFIG_FILE = "config.json"
SETUP_STATUS_FILE = "setup_status.json"

def reset_app():
    """Resets the application and returns a list of status messages."""
    messages = []

    try:
        # Reset configuration file
        if os.path.exists(CONFIG_FILE):
            messages.append(f"Deleting existing configuration: {CONFIG_FILE}")
            os.remove(CONFIG_FILE)
        with open(CONFIG_FILE, "w") as file:
            json.dump(DEFAULT_CONFIG, file, indent=4)
        messages.append(f"Default configuration saved in {CONFIG_FILE}.")

        # Reset setup status file
        if os.path.exists(SETUP_STATUS_FILE):
            messages.append(f"Deleting existing setup status file: {SETUP_STATUS_FILE}")
            os.remove(SETUP_STATUS_FILE)
        else:
            messages.append(f"No setup status file found ({SETUP_STATUS_FILE}).")

        messages.append("Reset complete. The app has been restored to its original state.")
    except Exception as e:
        messages.append(f"Error during reset: {str(e)}")

    return messages
