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

def reset_app(output_box):
    """Setzt die App zurück und schreibt die Ausgabe in die output_box."""
    if output_box is None:
        raise ValueError("output_box darf nicht None sein!")

    output_box.append("Starte Reset...")

    # Reset der Konfigurationsdatei
    if os.path.exists(CONFIG_FILE):
        output_box.append(f"Lösche bestehende Konfiguration: {CONFIG_FILE}")
        os.remove(CONFIG_FILE)
    with open(CONFIG_FILE, "w") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)
    output_box.append(f"Standardkonfiguration gespeichert in {CONFIG_FILE}.")

    # Reset der Setup-Status-Datei
    if os.path.exists(SETUP_STATUS_FILE):
        output_box.append(f"Lösche bestehende Setup-Status-Datei: {SETUP_STATUS_FILE}")
        os.remove(SETUP_STATUS_FILE)
    else:
        output_box.append(f"Keine Setup-Status-Datei gefunden ({SETUP_STATUS_FILE}).")

    output_box.append("Reset abgeschlossen. Die App wurde in den Originalzustand zurückgesetzt.")
