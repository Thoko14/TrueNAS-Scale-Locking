import paramiko
from config import load_config, decrypt_password

def execute_ssh_command(command):
    """Executes an SSH command on the TrueNAS server and returns the output."""
    client = None
    try:
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
        output = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            raise RuntimeError(f"SSH Command Error: {error}")

        return output
    except Exception as e:
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
