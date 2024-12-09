import json
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QLabel, QHBoxLayout, QPushButton
from config import encrypt_password, CONFIG_FILE

class SetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TrueNAS Setup")
        self.setModal(True)

        self.layout = QVBoxLayout()

        # Allgemeine Einstellungen
        self.host_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.pool_input = QLineEdit()

        general_layout = QFormLayout()
        general_layout.addRow("Host-IP:", self.host_input)
        general_layout.addRow("Benutzername:", self.username_input)
        general_layout.addRow("SSH-Passwort:", self.password_input)
        general_layout.addRow("Pool-Name:", self.pool_input)
        self.layout.addLayout(general_layout)

        # Dataset-Felder
        self.datasets_layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Datasets:"))
        self.layout.addLayout(self.datasets_layout)

        self.add_dataset_field("", None)

        add_button = QPushButton("+ Dataset hinzufügen")
        add_button.clicked.connect(lambda: self.add_dataset_field("", None))
        self.layout.addWidget(add_button)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

        self.setLayout(self.layout)

    def add_dataset_field(self, name, password):
        """Fügt ein neues Dataset-Feld hinzu."""
        dataset_layout = QHBoxLayout()
        name_input = QLineEdit(name)
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        dataset_layout.addWidget(QLabel("Name:"))
        dataset_layout.addWidget(name_input)
        dataset_layout.addWidget(QLabel("Passwort:"))
        dataset_layout.addWidget(password_input)
        self.datasets_layout.addLayout(dataset_layout)

    def accept(self):
        """Speichert die Konfiguration in der Datei."""
        config = {
            "host": self.host_input.text(),
            "username": self.username_input.text(),
            "password": encrypt_password(self.password_input.text()) if self.password_input.text() else None,
            "pool": self.pool_input.text(),
            "datasets": []
        }

        for i in range(self.datasets_layout.count()):
            layout = self.datasets_layout.itemAt(i).layout()
            if layout:
                name = layout.itemAt(1).widget().text()
                password = layout.itemAt(3).widget().text()
                config["datasets"].append({
                    "name": name,
                    "password": encrypt_password(password) if password else None
                })

        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file)

        self.done(1)  # Dialog schließen und Erfolg zurückgeben

def main():
    app = QApplication(sys.argv)
    setup_dialog = SetupDialog()
    if setup_dialog.exec_():
        print("Setup abgeschlossen. Konfiguration gespeichert.")
    else:
        print("Setup abgebrochen.")
    sys.exit()

if __name__ == "__main__":
    main()
