#Setup dialog

import json
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QLabel, QMessageBox
from app.utils.config import CONFIG_FILE
import requests

class SetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TrueNAS Setup")
        self.setModal(True)

        self.layout = QVBoxLayout()

        # General Settings
        self.host_input = QLineEdit()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)

        general_layout = QFormLayout()
        general_layout.addRow("Host-IP:", self.host_input)
        general_layout.addRow("API Key:", self.api_key_input)
        self.layout.addLayout(general_layout)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

        self.setLayout(self.layout)

    def validate_inputs(self):
        """Validates the inputs provided in the setup dialog."""
        host = self.host_input.text().strip()
        api_key = self.api_key_input.text().strip()

        if not host:
            QMessageBox.warning(self, "Validation Error", "Host-IP cannot be empty.")
            return False

        if not api_key:
            QMessageBox.warning(self, "Validation Error", "API Key cannot be empty.")
            return False

        try:
            response = requests.get(f"http://{host}/api/v2.0/system/info", headers={"Authorization": f"Bearer {api_key}"}, timeout=5)
            if response.status_code != 200:
                QMessageBox.warning(self, "Validation Error", "Failed to connect to the TrueNAS server. Please check the Host-IP and API Key.")
                return False
        except requests.RequestException as e:
            QMessageBox.warning(self, "Validation Error", f"Error connecting to the server: {e}")
            return False

        return True

    def accept(self):
        """Validates inputs and saves the configuration to the file."""
        if not self.validate_inputs():
            return

        config = {
            "host": self.host_input.text().strip(),
            "api_key": self.api_key_input.text().strip()
        }

        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)

        self.done(1)  # Close the dialog and signal success

def main():
    app = QApplication(sys.argv)
    setup_dialog = SetupDialog()
    if setup_dialog.exec_():
        print("Setup completed successfully. Configuration saved.")
    else:
        print("Setup canceled.")
    sys.exit()

if __name__ == "__main__":
    main()
