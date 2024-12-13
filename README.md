# TrueNAS Dataset Manager

## Overview
The TrueNAS Dataset Manager is a Python-based GUI application for managing TrueNAS Scale datasets. It simplifies locking, unlocking, and checking the status of datasets and provides additional features such as server reboot/shutdown.

## Features
- **Lock and Unlock Datasets:** Secure datasets with encryption or make them accessible when needed.
- **System Status Monitoring:** View the current status of datasets and TrueNAS server events.
- **Server Management:** Reboot or shut down the TrueNAS server directly from the application.
- **Performance Metrics:** Visualize CPU usage, disk I/O, and network traffic in real time.
- **Event Filtering:** Focus on new system events since the last session.

## Installation
### Prerequisites
- Python 3.9 or higher
- TrueNAS Scale accessible via SSH

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TrueNAS-Dataset-Manager.git
   ```
2. Navigate to the project directory:
   ```bash
   cd TrueNAS-Dataset-Manager
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Configuration
On the first run, a setup dialog will prompt you to configure your TrueNAS server:
- Host IP
- SSH Username and Password
- Pool Name
- Datasets (names and optional passwords)

The configuration is stored in `config.json` with encrypted passwords.

## Usage
1. **Lock Datasets:** Secure your datasets by clicking the "Lock Datasets" button.
2. **Unlock Datasets:** Make datasets accessible with the "Unlock Datasets" button. Passwords will be requested if not stored in the configuration.
3. **Check Status:** View the current status of datasets and server activities.
4. **Reboot/Shutdown:** Manage server power with the "Reboot Server" or "Shutdown Server" options.

## File Structure
- `main.py`: Entry point of the application.
- `config.py`: Handles configuration loading, saving, and encryption.
- `dialogs.py`: Manages GUI dialogs for configuration and interaction.
- `ssh_commands.py`: Executes SSH commands on the TrueNAS server.
- `reset_utils.py`: Resets the application to its original state.
- `requirements.txt`: Lists Python dependencies.

## Security
- **Encryption:** All passwords are securely encrypted using the Fernet encryption standard.
- **Secure Connections:** SSH commands are executed securely via the Paramiko library.

## Contributing
We welcome contributions! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Submit a pull request with a clear description of your changes.

## License
This project is licensed under a custom **Non-Commercial Open Source License**. See the `LICENSE` file for details.

## Acknowledgments
- [PyQt5](https://pypi.org/project/PyQt5/) for the GUI framework.
- [Paramiko](https://pypi.org/project/paramiko/) for SSH functionality.
- [Cryptography](https://pypi.org/project/cryptography/) for secure password management.

