import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, QWidget, QAction, QMessageBox
)
from config import CONFIG_FILE, load_config
from dialogs import ConfigDialog
from reset_utils import reset_app

class TrueNASManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()  # Lade die Konfiguration
        self.setWindowTitle("TrueNAS Dataset Manager")
        self.setGeometry(100, 100, 500, 400)
        self.center_window()

        self.init_ui()

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

        # Lock-, Unlock- und Status-Buttons
        lock_button = QPushButton("Lock Datasets")
        lock_button.clicked.connect(lambda: self.output_box.append("Locking datasets... (not implemented)"))
        layout.addWidget(lock_button)

        unlock_button = QPushButton("Unlock Datasets")
        unlock_button.clicked.connect(lambda: self.output_box.append("Unlocking datasets... (not implemented)"))
        layout.addWidget(unlock_button)

        status_button = QPushButton("Status prüfen")
        status_button.clicked.connect(lambda: self.output_box.append("Checking status... (not implemented)"))
        layout.addWidget(status_button)

        # Ausgabe-Box
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        layout.addWidget(QLabel("Ausgabe:"))
        layout.addWidget(self.output_box)

        # Menüleiste erstellen
        if not hasattr(self, "menu_initialized"):
            self.menu_initialized = True
            menu_bar = self.menuBar()
            settings_menu = menu_bar.addMenu("Einstellungen")

            # Menüpunkt: Konfiguration
            config_action = QAction("Konfiguration", self)
            config_action.triggered.connect(self.open_config_dialog)
            settings_menu.addAction(config_action)

            # Menüpunkt: App Zurücksetzen
            reset_action = QAction("App Zurücksetzen", self)
            reset_action.triggered.connect(self.confirm_reset)
            settings_menu.addAction(reset_action)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def open_config_dialog(self):
        """Öffnet das Konfigurationsdialogfenster."""
        print("Öffne Konfigurationsdialog...")
        config_dialog = ConfigDialog(self)
        if config_dialog.exec_():
            print("Konfigurationsdialog erfolgreich abgeschlossen.")
            self.init_ui()  # UI nach Konfigurationsänderungen aktualisieren
        else:
            print("Konfigurationsdialog abgebrochen.")

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
            reset_app(self.output_box)  # Übergibt die output_box an reset_app
            self.output_box.append("Reset erfolgreich abgeschlossen.")


    def center_window(self):
        """Platziert das Fenster in der Mitte des Bildschirms."""
        screen_geometry = QApplication.desktop().screenGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

def initialize_app():
    """Überprüft, ob die Konfiguration existiert, und führt ggf. das Setup durch."""
    if not os.path.exists(CONFIG_FILE):
        print("Keine Konfiguration gefunden. Starte Setup...")
        from setup import SetupDialog
        app = QApplication(sys.argv)
        setup_dialog = SetupDialog()
        if setup_dialog.exec_():
            print("Setup abgeschlossen. Anwendung wird gestartet.")
        else:
            print("Setup abgebrochen. Anwendung wird beendet.")
            sys.exit()

def main():
    """Startet die Hauptanwendung."""
    initialize_app()
    app = QApplication(sys.argv)
    main_window = TrueNASManager()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
