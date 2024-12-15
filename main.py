import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QHeaderView,QTableWidgetItem,
    QVBoxLayout, QLabel, QPushButton, QWidget, QAction, QMessageBox, QTextEdit, QInputDialog
)
from PyQt5.QtCore import QTimer
from config import load_config, decrypt_password
from ssh_commands import execute_ssh_command, fetch_smart_data, fetch_smart_details
from dialogs import ConfigDialog
from reset_utils import reset_app
from performance_visualisation import PerformanceVisualisation

class TrueNASManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle("TrueNAS Dataset Manager")
        self.setGeometry(100, 100, 800, 600)
        self.center_window()
        self.init_ui()
        
        # Try to fetch SMART data on startup
        try:
            self.update_smart_table()
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Could not connect to TrueNAS: {str(e)}")

    
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche."""
        main_widget = QWidget()
        layout = QVBoxLayout()

        # Anzeige von IP, Pool und Datasets
        layout.addWidget(QLabel(f"Host-IP: {self.config['host']}"))
        layout.addWidget(QLabel(f"Pool-Name: {self.config['pool']}"))
        datasets_label = QLabel(f"Datasets: {', '.join([ds['name'] for ds in self.config['datasets']])}")
        datasets_label.setWordWrap(True)
        layout.addWidget(datasets_label)

        # Add Performance Visualisation
        self.performance_visualisation = PerformanceVisualisation()
        layout.addWidget(self.performance_visualisation)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Set up a timer to update metrics periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_performance_metrics)
        self.timer.start(1000)  # Update every 1 second

        # SMART Table
        self.smart_table = QTableWidget()
        self.smart_table.setColumnCount(4)
        self.smart_table.setHorizontalHeaderLabels(["Drive", "Temperature", "Health", "Actions"])
        self.smart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel("SMART Report:"))
        layout.addWidget(self.smart_table)
                
        # Lock-, Unlock- und Status-Buttons
        lock_button = QPushButton("Lock Datasets")
        lock_button.clicked.connect(self.lock_datasets)
        layout.addWidget(lock_button)

        unlock_button = QPushButton("Unlock Datasets")
        unlock_button.clicked.connect(self.unlock_datasets)
        layout.addWidget(unlock_button)

        status_button = QPushButton("Check Status")
        status_button.clicked.connect(self.check_status)
        layout.addWidget(status_button)

        # Ausgabe-Box
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output_box)

        # Menüleiste erstellen
        if not hasattr(self, "menu_initialized"):
            self.menu_initialized = True
            menu_bar = self.menuBar()

            # Einstellungen
            settings_menu = menu_bar.addMenu("Einstellungen")
            config_action = QAction("Konfiguration", self)
            config_action.triggered.connect(self.open_config_dialog)
            settings_menu.addAction(config_action)

            reset_action = QAction("App Zurücksetzen", self)
            reset_action.triggered.connect(self.confirm_reset)
            settings_menu.addAction(reset_action)

            # Systemsteuerung
            system_menu = menu_bar.addMenu("Systemsteuerung")
            reboot_action = QAction("Reboot", self)
            reboot_action.triggered.connect(self.confirm_reboot)
            system_menu.addAction(reboot_action)

            shutdown_action = QAction("Shutdown", self)
            shutdown_action.triggered.connect(self.confirm_shutdown)
            system_menu.addAction(shutdown_action)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def update_performance_metrics(self):
        """Updates the performance metrics."""
        self.performance_visualisation.update_metrics()
        
    def lock_datasets(self):
        """Verschlüsselt die Datasets."""
        self.output_box.append("Locking datasets...")
        for dataset in self.config['datasets']:
            dataset_name = dataset['name']
            self.output_box.append(f"Locking dataset: {dataset_name}...")
            execute_ssh_command(f"zfs unload-key -r {self.config['pool']}/{dataset_name}", self.output_box)

    def unlock_datasets(self):
        """Entschlüsselt die Datasets."""
        self.output_box.append("Unlocking datasets...")
        for dataset in self.config['datasets']:
            dataset_name = dataset['name']
            password = dataset.get('password')
            if not password:
                password, ok = QInputDialog.getText(self, "Passwort erforderlich", f"Passwort für Dataset {dataset_name} eingeben:", QInputDialog.Password)
                if not ok or not password:
                    self.output_box.append(f"Überspringe Dataset: {dataset_name} (kein Passwort eingegeben).")
                    continue
            else:
                password = decrypt_password(password)

            self.output_box.append(f"Unlocking dataset: {dataset_name}...")
            execute_ssh_command(f"echo {password} | zfs load-key -r {self.config['pool']}/{dataset_name}", self.output_box)

    def check_status(self):
        """Prüft den Status des Systems."""
        self.output_box.append("Prüfe Systemstatus...")
        execute_ssh_command("zfs list", self.output_box)

    def open_config_dialog(self):
        """Öffnet das Konfigurationsdialogfenster."""
        config_dialog = ConfigDialog(self)
        if config_dialog.exec_():
            self.config = load_config()  # Aktualisiere die Konfiguration
            self.init_ui()

    def confirm_reset(self):
        """Zeigt eine Warnung an und setzt die App zurück."""
        reply = QMessageBox.warning(
            self,
            "App zurücksetzen",
            "Sind Sie sicher, dass Sie die App in den Originalzustand zurücksetzen möchten? "
            "Alle Konfigurationen werden gelöscht.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            reset_app(self.output_box)
            self.output_box.append("Reset erfolgreich abgeschlossen.")

    def confirm_reboot(self):
        """Zeigt eine Warnung an und startet das System neu."""
        reply = QMessageBox.warning(
            self,
            "System neu starten",
            "Sind Sie sicher, dass Sie den TrueNAS-Server neu starten möchten?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.output_box.append("Starte System neu...")
            execute_ssh_command("reboot", self.output_box)

    def confirm_shutdown(self):
        """Zeigt eine Warnung an und fährt das System herunter."""
        reply = QMessageBox.warning(
            self,
            "System herunterfahren",
            "Sind Sie sicher, dass Sie den TrueNAS-Server herunterfahren möchten?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.output_box.append("Fahre System herunter...")
            execute_ssh_command("shutdown now", self.output_box)

    def center_window(self):
        """Platziert das Fenster in der Mitte des Bildschirms."""
        screen_geometry = QApplication.desktop().screenGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def update_smart_table(self):
        """Fetches and updates the SMART table."""
        smart_data = fetch_smart_data()
        self.smart_table.setRowCount(len(smart_data))
        for row, drive in enumerate(smart_data):
            self.smart_table.setItem(row, 0, QTableWidgetItem(drive["name"]))
            self.smart_table.setItem(row, 1, QTableWidgetItem(drive["temperature"]))
            self.smart_table.setItem(row, 2, QTableWidgetItem(drive["health"]))

            # Details Button
            details_button = QPushButton("Details")
            details_button.clicked.connect(lambda _, d=drive["name"]: self.show_smart_details(d))
            self.smart_table.setCellWidget(row, 3, details_button)

    def show_smart_details(self, drive_name):
        """Opens a dialog showing detailed SMART data for a drive."""
        try:
            details = fetch_smart_details(drive_name)
            QMessageBox.information(self, f"SMART Details for {drive_name}", details)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not fetch SMART details: {str(e)}")


def initialize_app():
    """Überprüft, ob die Konfiguration existiert und gültig ist, und führt ggf. das Setup durch."""
    try:
        config = load_config()
        if not config.get("host") or not config.get("pool") or not config.get("datasets"):
            raise ValueError("Ungültige oder unvollständige Konfiguration.")
    except (FileNotFoundError, ValueError):
        from setup import SetupDialog
        app = QApplication(sys.argv)
        setup_dialog = SetupDialog()
        if setup_dialog.exec_():
            print("Setup abgeschlossen. Anwendung wird gestartet.")
        else:
            sys.exit("Setup abgebrochen.")

def main():
    """Startet die Hauptanwendung."""
    initialize_app()
    app = QApplication(sys.argv)
    main_window = TrueNASManager()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
