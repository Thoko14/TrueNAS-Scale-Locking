import requests
from app.utils.config import get_api_key, get_api_url
from datetime import datetime
from app.utils.timestamp import save_last_alert_check_time, load_last_alert_check_time

def fetch_new_alerts():
    """Fetches new alerts from the TrueNAS API based on the last check time."""
    try:
        api_url = get_api_url()
        headers = get_headers()

        # Fetch last check time
        last_check_time = load_last_alert_check_time()

        # Fetch all alerts
        response = requests.get(f"{api_url}/alert/list/", headers=headers)
        response.raise_for_status()

        alerts = response.json()

        # Filter alerts based on the last check time
        new_alerts = []
        for alert in alerts:
            alert_time_str = alert.get("datetime")
            if alert_time_str:
                alert_time = datetime.fromisoformat(alert_time_str)
                if last_check_time is None or alert_time > last_check_time:
                    new_alerts.append(alert)

        # Save the current time as the new last check time
        save_last_alert_check_time(datetime.now())

        return new_alerts
    except requests.exceptions.RequestException as e:
        print(f"Error fetching new alerts: {e}")
        return []

def fetch_network_stats():
    """Fetch network statistics (e.g., throughput) from TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()

        # Fetch network stats using the reporting API
        payload = {"name": "network"}
        response = requests.post(f"{api_url}/reporting/get_data/", headers=headers, json=payload)
        response.raise_for_status()

        # Parse and return the network statistics
        network_stats = response.json()
        return network_stats
    except requests.exceptions.RequestException as e:
        print(f"Error fetching network stats: {e}")
        return None

def get_headers():
    """Retrieve headers for API requests."""
    api_key = get_api_key()
    return {
        "Authorization": f"Bearer {api_key}"
    }

def fetch_disk_stats():
    """Fetch disk statistics (e.g., I/O rates) from TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.get(f"{api_url}/disk/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching disk stats: {e}")
        return None

def fetch_system_info():
    """Fetch system information (CPU load, memory, etc.) from TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.get(f"{api_url}/system/info", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching system info: {e}")
        return None


def fetch_smart_data():
    """Fetch SMART data for all disks from TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.get(f"{api_url}/disk/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SMART data: {e}")
        return None


def fetch_system_logs():
    """Fetch system logs from TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.get(f"{api_url}/system/log/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching system logs: {e}")
        return None


def fetch_alerts():
    """Fetch active alerts from TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.get(f"{api_url}/alert/list/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching alerts: {e}")
        return None


def fetch_datasets():
    """Fetch all datasets and their properties from TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.get(f"{api_url}/pool/dataset/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching datasets: {e}")
        return None


def lock_dataset(dataset_name):
    """Lock a specific dataset using the TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.post(f"{api_url}/pool/dataset/id/{dataset_name}/lock", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error locking dataset: {e}")
        return None


def unlock_dataset(dataset_name, password):
    """Unlock a specific dataset using the TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        payload = {"password": password}
        response = requests.post(f"{api_url}/pool/dataset/id/{dataset_name}/unlock", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error unlocking dataset: {e}")
        return None


def reboot_system():
    """Reboot the TrueNAS server using the API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.post(f"{api_url}/system/reboot/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error rebooting system: {e}")
        return None


def shutdown_system():
    """Shutdown the TrueNAS server using the API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.post(f"{api_url}/system/shutdown/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error shutting down system: {e}")
        return None

def fetch_messages_log():
    """Fetch system messages log from TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()

        # Fetch system log messages
        response = requests.get(f"{api_url}/system/log/", headers=headers)
        response.raise_for_status()

        logs = response.json()  # Expect logs to be a list of messages
        formatted_logs = "\n".join([log.get("message", "No message") for log in logs])

        return formatted_logs
    except requests.exceptions.RequestException as e:
        print(f"Error fetching system messages log: {e}")
        return "Error fetching system logs."
    
def fetch_alerts_log():
    """Fetches and formats the alerts log from the TrueNAS API."""
    try:
        api_url = get_api_url()
        headers = get_headers()

        # Fetch alerts
        response = requests.get(f"{api_url}/alert/list/", headers=headers)
        response.raise_for_status()

        alerts = response.json()  # List of alert objects
        formatted_alerts = "\n".join(
            [f"{alert.get('datetime')} - {alert.get('level').upper()}: {alert.get('formatted')}" for alert in alerts]
        )

        return formatted_alerts
    except requests.exceptions.RequestException as e:
        print(f"Error fetching alerts log: {e}")
        return "Error fetching alerts log."

def reboot_system():
    """Reboot the TrueNAS server using the API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.post(f"{api_url}/system/reboot/", headers=headers)
        response.raise_for_status()
        return "reboot"
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error rebooting system: {e}")


def shutdown_system():
    """Shutdown the TrueNAS server using the API."""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.post(f"{api_url}/system/shutdown/", headers=headers)
        response.raise_for_status()
        return "shutdown"
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error shutting down system: {e}")

