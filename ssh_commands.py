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

def fetch_smart_data():
    """Fetches SMART data for all drives."""
    command = "smartctl --scan"
    output = execute_ssh_command(command)

    drives = []
    for line in output.splitlines():
        if "/dev" in line:
            drive_name = line.split()[0]
            smart_info = execute_ssh_command(f"smartctl -a {drive_name}")
            drives.append({
                "name": drive_name,
                "temperature": parse_smart_temperature(smart_info),
                "health": parse_smart_health(smart_info),
            })
    return drives


def fetch_smart_details(drive_name):
    """Fetches detailed SMART data for a specific drive."""
    command = f"smartctl -a {drive_name}"
    return execute_ssh_command(command)


def parse_smart_temperature(smart_info):
    """Parses temperature from SMART output."""
    for line in smart_info.splitlines():
        if "Temperature" in line:
            return line.split(":")[-1].strip()
    return "N/A"


def parse_smart_health(smart_info):
    """Parses health status from SMART output."""
    for line in smart_info.splitlines():
        if "SMART overall-health" in line:
            return line.split(":")[-1].strip()
    return "N/A"
