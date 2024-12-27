# Dark mode utilities
import json
import os

DARK_MODE_STATE_FILE = "dark_mode_state.json"

def save_dark_mode_state(enabled):
    """Saves the dark mode state to a file."""
    with open(DARK_MODE_STATE_FILE, "w") as file:
        json.dump({"dark_mode": enabled}, file)

def load_dark_mode_state():
    """Loads the dark mode state from a file."""
    if os.path.exists(DARK_MODE_STATE_FILE):
        with open(DARK_MODE_STATE_FILE, "r") as file:
            data = json.load(file)
            return data.get("dark_mode", False)  # Default to False
    return False
