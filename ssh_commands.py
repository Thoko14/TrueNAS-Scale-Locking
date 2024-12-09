import paramiko
from config import CONFIG, decrypt_password

def execute_ssh_command(action, output_box):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(CONFIG["host"], username=CONFIG["username"], password=decrypt_password(CONFIG["password"]) if CONFIG["password"] else None)

        output_box.clear()
        for dataset in CONFIG["datasets"]:
            dataset_name = dataset["name"]
            full_path = f"{CONFIG['pool']}/{dataset_name}"
            command = f"zfs {action}-key {full_path}"
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            if error:
                output_box.append(f"[Fehler bei {dataset_name}]: {error}")
            else:
                output_box.append(f"[Erfolg bei {dataset_name}]: {output}")
        ssh.close()
    except Exception as e:
        output_box.append(f"Verbindungsfehler: {str(e)}")

def check_status(output_box):
    execute_ssh_command("get keystatus", output_box)
