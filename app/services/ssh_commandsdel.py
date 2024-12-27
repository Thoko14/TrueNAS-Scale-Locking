import paramiko
import logging
import json
from datetime import datetime
from app.utils.config import load_config, decrypt_password
from app.utils.timestamp import load_last_alert_check_time, save_last_alert_check_time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def execute_ssh_command(command):
    """Executes an SSH command on the TrueNAS server and returns the output."""
    client = None
    try:
        logging.info(f"Executing command: {command}")
        config = load_config()
        hostname = config.get("host")
        username = config.get("username", "root")
        encrypted_password = config.get("password")

        if not hostname or not encrypted_password:
            raise ValueError("Hostname or password is missing in the configuration.")

        password = decrypt_password(encrypted_password)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname, username=username, password=password)

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode("utf-8", errors="replace")  # Use UTF-8 decoding
        error = stderr.read().decode("utf-8", errors="replace")  # Handle errors safely

        if error:
            logging.error(f"Error executing command: {error}")
            raise RuntimeError(f"SSH Command Error: {error}")

        logging.info(f"Command output: {output}")
        return output
    except Exception as e:
        logging.error(f"SSH Execution Failed: {str(e)}")
        raise RuntimeError(f"SSH Execution Failed: {str(e)}")
    finally:
        if client:
            client.close()


def check_status():
    """Executes the system status command and returns the results."""
    return execute_ssh_command("systemctl status")

def fetch_smart_data():
    """Fetches SMART data for all drives."""
    command = "smartctl --scan"
    scan_output = execute_ssh_command(command)

    drives = []
    for line in scan_output.splitlines():
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

def fetch_messages_log():
    """Fetches only the system messages log."""
    try:
        # Fetch system messages safely
        messages_command = "sudo cat /var/log/messages"
        messages_output = execute_ssh_command(messages_command)
        safe_messages = messages_output.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
        return f"===== System Messages =====\n{safe_messages}"
    except Exception as e:
        raise RuntimeError(f"Error fetching system messages log: {str(e)}")

def fetch_alerts_log():
    """Fetches only the TrueNAS alerts log."""
    import json
    from datetime import datetime

    try:
        # Fetch alerts safely
        alerts_command = "sudo midclt call alert.list"
        alerts_output = execute_ssh_command(alerts_command)

        # Parse alerts into readable format
        alerts_log = ""
        try:
            alerts = json.loads(alerts_output)
            if not alerts:
                alerts_log = "No active alerts found.\n"
            else:
                for alert in alerts:
                    raw_date = alert.get("datetime", {}).get("$date", 0)
                    readable_date = datetime.fromtimestamp(raw_date / 1000).isoformat() if raw_date else "Unknown time"
                    level = alert.get("level", "INFO").upper()
                    formatted_message = alert.get("formatted", "No message available")
                    alerts_log += f"{readable_date} - {level}: {formatted_message}\n"
        except json.JSONDecodeError:
            alerts_log = "Error parsing alerts log."

        return f"===== Alerts =====\n{alerts_log}"
    except Exception as e:
        raise RuntimeError(f"Error fetching alerts log: {str(e)}")

import os
import json
from datetime import datetime

def fetch_combined_server_logs():
    """Fetches and combines logs from /var/log/messages and TrueNAS alerts, saving them locally."""

    try:
        # Step 1: Fetch system messages
        messages_command = "sudo cat /var/log/messages"
        messages_output = execute_ssh_command(messages_command)
        safe_messages = messages_output.encode("utf-8", errors="replace").decode("utf-8", errors="replace")

        # Step 2: Fetch alerts from TrueNAS
        alerts_command = "sudo midclt call alert.list"
        alerts_output = execute_ssh_command(alerts_command)
        alerts_log = ""

        # Step 3: Process alerts
        try:
            alerts = json.loads(alerts_output)
            if not alerts:
                alerts_log = "No active alerts found.\n"
            else:
                for alert in alerts:
                    raw_date = alert.get("datetime", {}).get("$date", 0)
                    readable_date = datetime.fromtimestamp(raw_date / 1000).isoformat() if raw_date else "Unknown time"
                    level = alert.get("level", "INFO").upper()
                    formatted_message = alert.get("formatted", "No message available")
                    alerts_log += f"{readable_date} - {level}: {formatted_message}\n"
        except json.JSONDecodeError:
            alerts_log = "Error parsing alerts log."

        # Step 4: Combine logs
        combined_logs = f"===== System Messages =====\n{safe_messages}\n\n===== Alerts =====\n{alerts_log}"
        safe_combined_logs = combined_logs.encode("utf-8", errors="replace").decode("utf-8", errors="replace")

        # Step 5: Save to local file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        SERVER_LOG_FILE = os.path.join(BASE_DIR, "server.log")

        with open(SERVER_LOG_FILE, "w", encoding="utf-8", errors="replace") as file:
            file.write(safe_combined_logs)

        return SERVER_LOG_FILE  # Return the file path for display

    except Exception as e:
        raise RuntimeError(f"Error fetching combined server logs: {str(e)}")



def fetch_new_alerts():
    """Fetches new alerts from the TrueNAS server."""
    try:
        # Load the last check timestamp
        last_check_timestamp = load_last_alert_check_time()

        # Fetch alerts using the TrueNAS middleware command
        command = "midclt call alert.list"
        output = execute_ssh_command(command)

        # Parse the JSON response
        alerts = json.loads(output)

        # Filter alerts based on timestamp
        new_alerts = []
        for alert in alerts:
            alert_time = datetime.strptime(alert["datetime"], "%Y-%m-%dT%H:%M:%S")
            if last_check_timestamp is None or alert_time > last_check_timestamp:
                new_alerts.append(alert)

        # Update the last check timestamp
        if new_alerts:
            latest_alert_time = max(datetime.strptime(alert["datetime"], "%Y-%m-%dT%H:%M:%S") for alert in new_alerts)
            save_last_alert_check_time(latest_alert_time)

        return new_alerts
    except Exception as e:
        raise RuntimeError(f"Error fetching new alerts: {str(e)}")

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

def fetch_datasets():
    """Fetches all datasets and their encryption states."""
    command = "zfs list -o name,encryption,keystatus -H"
    output = execute_ssh_command(command)

    datasets = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            name, encryption, keystatus = parts
            datasets.append({
                "name": name.strip(),
                "encryption": encryption.strip() == "on",
                "keystatus": keystatus.strip()
            })
    return datasets

def lock_dataset(dataset_name):
    """Locks a specific dataset."""
    command = f"zfs unload-key -r {dataset_name}"
    execute_ssh_command(command)

def unlock_dataset(dataset_name, password):
    """Unlocks a specific dataset using the provided password."""
    command = f"echo {password} | zfs load-key -r {dataset_name}"
    execute_ssh_command(command)

def reboot_system():
    """Reboots the TrueNAS server."""
    return execute_ssh_command("reboot")

def shutdown_system():
    """Shuts down the TrueNAS server."""
    return execute_ssh_command("shutdown now")
