import json
from cryptography.fernet import Fernet

# Encryption Key
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


ENCRYPTION_KEY = get_encryption_key()
FERNET = Fernet(ENCRYPTION_KEY)

def load_config():
    """Loads the configuration file."""
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "host": "",
            "username": "",
            "password": None,
            "pool": "",
            "datasets": []
        }

# Save configuration
def save_config(config):
    """Speichert die Konfigurationsdatei."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

# Encrypt and decrypt passwords
def encrypt_password(password):
    return FERNET.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return FERNET.decrypt(encrypted_password.encode()).decode()
