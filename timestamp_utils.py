import json
import os
from datetime import datetime

LAST_ALERT_CHECK_FILE = "last_alert_check.json"

def save_last_alert_check_time(timestamp):
    """
    Saves the last check timestamp as ISO 8601 string.
    Args:
        timestamp (datetime): The timestamp to save.
    """
    with open(LAST_ALERT_CHECK_FILE, "w") as file:
        json.dump({"last_check_time": timestamp.isoformat()}, file)

def load_last_alert_check_time():
    """
    Loads the last check timestamp as a datetime object.
    Returns:
        datetime: The last check timestamp, or datetime.min if not available.
    """
    if os.path.exists(LAST_ALERT_CHECK_FILE):
        with open(LAST_ALERT_CHECK_FILE, "r") as file:
            data = json.load(file)
            last_check_time = data.get("last_check_time")
            if last_check_time:
                return datetime.fromisoformat(last_check_time)
    return datetime.min  # Default value if no timestamp exists
