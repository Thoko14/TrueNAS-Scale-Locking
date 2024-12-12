import paramiko
from config import load_config, decrypt_password

def execute_ssh_command(command, output_box):
    """Führt einen SSH-Befehl auf dem TrueNAS-Server aus."""
    client = None
    try:
        config = load_config()
        hostname = config.get("host")
        username = config.get("username", "root")
        encrypted_password = config.get("password")

        if not hostname or not encrypted_password:
            output_box.append("Fehler: Hostname oder Passwort fehlen in der Konfiguration.")
            return

        password = decrypt_password(encrypted_password)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname, username=username, password=password)

        stdin, stdout, stderr = client.exec_command(command)
        output_box.append(f"Befehl: {command} wird ausgeführt...\n")
        output_box.append(stdout.read().decode())
        output_box.append(stderr.read().decode())
    except Exception as e:
        output_box.append(f"Fehler: {str(e)}")
    finally:
        if client:  # Überprüfe, ob der Client initialisiert wurde
            client.close()

def check_status(output_box):
    """Führt den Statusbefehl aus und gibt die Ergebnisse aus."""
    execute_ssh_command("systemctl status", output_box)
