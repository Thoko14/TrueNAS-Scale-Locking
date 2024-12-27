# Configuration management

import json
from cryptography.fernet import Fernet

# File Paths
KEY_FILE = "encryption_key.key"
CONFIG_FILE = "config.json"

# Generate or load an encryption key
def get_encryption_key():
    try:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
            # Validate key
            if len(key) != 44:  # Fernet keys are 44 bytes in base64
                raise ValueError("Invalid key length.")
            return key
    except (FileNotFoundError, ValueError):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

# Initialize encryption key
ENCRYPTION_KEY = get_encryption_key()
FERNET = Fernet(ENCRYPTION_KEY)

def load_config():
    """Loads the configuration file."""
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError("Configuration file not found. Setup is required.")

def save_config(config):
    """Saves the configuration file."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

# Encrypt and decrypt passwords
def encrypt_password(password):
    return FERNET.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return FERNET.decrypt(encrypted_password.encode()).decode()

def get_api_key():
    """Retrieves the API key from the configuration file."""
    config = load_config()
    api_key = config.get("api_key")
    if not api_key:
        raise ValueError("API key is missing in the configuration file.")
    return api_key

def get_api_url():
    """Retrieves the base API URL from the configuration file."""
    config = load_config()
    api_url = config.get("host", "").strip()

    # Ensure the URL includes a scheme
    if not api_url.startswith(("http://", "https://")):
        api_url = f"http://{api_url}"  # Default to http:// if no scheme is provided

    # Append API prefix if missing
    if not api_url.endswith("/api/v2.0"):
        api_url = f"{api_url.rstrip('/')}/api/v2.0"

    return api_url


