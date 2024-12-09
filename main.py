import os
import json
import sys
from PyQt5.QtWidgets import (
    QAction, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QDialogButtonBox, QLabel, QPushButton, QMessageBox, QWidget, 
    QSpacerItem, QSizePolicy, QTextEdit
)
from config import CONFIG, save_config
from dialogs import ConfigDialog
from ssh_commands import execute_ssh_command, check_status


SETUP_STATUS_FILE = "setup_status.json"

def is_setup_completed():
    """Überprüft, ob das Setup abgeschlossen ist."""
    if not os.path.exists(SETUP_STATUS_FILE):
        return False
    with open(SETUP_STATUS_FILE, "r") as file:
        data = json.load(file)
        return data.get("setup_completed", False)

def mark_setup_completed():
    """Markiert das Setup als abgeschlossen."""
    with open(SETUP_STATUS_FILE, "w") as file:
        json.dump({"setup_completed": True}, file)

class TrueNASManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TrueNAS Dataset Manager")
        self.setGeometry(100, 100, 500, 400)
        self.center_window()

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()

        # Anzeige von IP, Pool und Datasets
        layout.addWidget(QLabel(f"Host-IP: {CONFIG['host']}"))
        layout.addWidget(QLabel(f"Pool-Name: {CONFIG['pool']}"))
        datasets_label = QLabel(f"Datasets: {', '.join([ds['name'] for ds in CONFIG['datasets']])}")
        datasets_label.setWordWrap(True)
        layout.addWidget(datasets_label)

        # Lock-, Unlock- und Status-Buttons
        lock_button = QPushButton("Lock Datasets")
        lock_button.clicked.connect(lambda: execute_ssh_command("unload", self.output_box))
        layout.addWidget(lock_button)

        unlock_button = QPushButton("Unlock Datasets")
        unlock_button.clicked.connect(lambda: execute_ssh_command("load", self.output_box))
        layout.addWidget(unlock_button)

        status_button = QPushButton("Status prüfen")
        status_button.clicked.connect(lambda: check_status(self.output_box))
        layout.addWidget(status_button)

        # Ausgabe-Box
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        layout.addWidget(QLabel("Ausgabe:"))
        layout.addWidget(self.output_box)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Menüleiste erstellen (nur einmal)
        if not hasattr(self, "menu_initialized"):
            self.menu_initialized = True
            menu_bar = self.menuBar()
            settings_menu = menu_bar.addMenu("Einstellungen")

            config_action = QAction("Konfiguration", self)
            config_action.triggered.connect(self.open_config_dialog)
            settings_menu.addAction(config_action)

    def open_config_dialog(self):
        config_dialog = ConfigDialog(self)
        if config_dialog.exec_():
            self.init_ui()  # Aktualisiere das UI nach Änderungen

    def center_window(self):
        """Platziert das Fenster in der Mitte des Bildschirms."""
        screen_geometry = QApplication.desktop().screenGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

def main():
    app = QApplication(sys.argv)

    # Setup ausführen, falls nicht abgeschlossen
    if not is_setup_completed():
        setup_dialog = ConfigDialog()
        if setup_dialog.exec_():
            mark_setup_completed()
        else:
            print("Setup abgebrochen.")
            return

    # Hauptanwendung starten
    main_window = TrueNASManager()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
