import json
import os

LAST_ALERT_CHECK_FILE = "last_alert_check.json"

def save_last_alert_check_time(timestamp):
    """Saves the last check timestamp."""
    with open(LAST_ALERT_CHECK_FILE, "w") as file:
        json.dump({"last_check_time": timestamp}, file)

def load_last_alert_check_time():
    """Loads the last check timestamp."""
    if os.path.exists(LAST_ALERT_CHECK_FILE):
        with open(LAST_ALERT_CHECK_FILE, "r") as file:
            data = json.load(file)
            return data.get("last_check_time", 0)  # Default to 0 if no timestamp
    return 0
