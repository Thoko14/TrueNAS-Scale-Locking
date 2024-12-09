import json
from cryptography.fernet import Fernet

# Verschlüsselungsschlüssel
KEY_FILE = "encryption_key.key"
CONFIG_FILE = "config.json"

# Erzeuge oder lade einen Verschlüsselungsschlüssel
def get_encryption_key():
    try:
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

ENCRYPTION_KEY = get_encryption_key()
FERNET = Fernet(ENCRYPTION_KEY)

# Konfiguration laden oder erstellen
def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "host": "192.168.2.71",
            "username": "root",
            "password": None,
            "pool": "TrueMirror",
            "datasets": [
                {"name": "DataNAS", "password": None},
                {"name": "Media", "password": None},
                {"name": "Memories", "password": None}
            ]
        }

CONFIG = load_config()

# Konfiguration speichern
def save_config():
    with open(CONFIG_FILE, "w") as file:
        json.dump(CONFIG, file)

# Verschlüsseln und Entschlüsseln von Passwörtern
def encrypt_password(password):
    return FERNET.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return FERNET.decrypt(encrypted_password.encode()).decode()
