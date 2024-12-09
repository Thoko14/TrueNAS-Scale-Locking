from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QDialogButtonBox,
    QLabel, QPushButton, QMessageBox, QApplication, QSpacerItem, QWidget, QSizePolicy
)
from config import CONFIG, save_config, encrypt_password

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konfiguration")
        self.setModal(True)

        self.main_layout = QVBoxLayout()  # Hauptlayout

        # Allgemeine Einstellungen in zwei Spalten
        general_layout = QHBoxLayout()

        # Linke Spalte: Host-IP und Benutzername
        left_layout = QVBoxLayout()
        self.host_input = QLineEdit(CONFIG["host"])
        self.username_input = QLineEdit(CONFIG["username"])
        left_layout.addWidget(QLabel("Host-IP:"))
        left_layout.addWidget(self.host_input)
        left_layout.addWidget(QLabel("Benutzername:"))
        left_layout.addWidget(self.username_input)

        # Rechte Spalte: Passwort und Pool-Name
        right_layout = QVBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.pool_input = QLineEdit(CONFIG["pool"])
        right_layout.addWidget(QLabel("Passwort:"))
        right_layout.addWidget(self.password_input)
        right_layout.addWidget(QLabel("Pool-Name:"))
        right_layout.addWidget(self.pool_input)

        # Spalten zusammenführen
        general_layout.addLayout(left_layout)
        general_layout.addSpacing(30)  # Abstand zwischen den Spalten
        general_layout.addLayout(right_layout)
        self.main_layout.addLayout(general_layout)

        # Fixiertes Label für Datasets
        label_layout = QHBoxLayout()
        self.datasets_label = QLabel("Datasets:")
        label_layout.addWidget(self.datasets_label)
        label_layout.addSpacerItem(QSpacerItem(40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addLayout(label_layout)

        # Dynamischer Bereich für Dataset-Felder
        self.datasets_widget = QWidget()
        self.datasets_layout = QVBoxLayout(self.datasets_widget)
        self.datasets_layout.setSpacing(10)  # Abstand zwischen den Datasets
        self.datasets_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.datasets_widget)

        # Vorhandene Datasets laden
        for dataset in CONFIG["datasets"]:
            self.add_dataset_field(dataset["name"], dataset["password"])

        # + Button zum Hinzufügen neuer Datasets
        add_button = QPushButton("+ Dataset hinzufügen")
        add_button.clicked.connect(lambda: self.add_dataset_field("", ""))
        self.main_layout.addWidget(add_button)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.main_layout.addWidget(buttons)

        self.setLayout(self.main_layout)

    def add_dataset_field(self, name="", password=""):
        """Fügt ein neues Dataset-Feld hinzu."""
        dataset_layout = QHBoxLayout()

        # Felder für Dataset
        name_input = QLineEdit(name)
        password_input = QLineEdit(password)
        password_input.setEchoMode(QLineEdit.Password)

        # Löschen-Button
        delete_button = QPushButton("Löschen")
        delete_button.clicked.connect(lambda: self.remove_dataset_field(dataset_layout))

        # Hinzufügen der Widgets zum Layout
        dataset_layout.addWidget(QLabel("Name:"))
        dataset_layout.addWidget(name_input)
        dataset_layout.addWidget(QLabel("Passwort:"))
        dataset_layout.addWidget(password_input)
        dataset_layout.addWidget(delete_button)

        # Layout zum Hauptlayout hinzufügen
        self.datasets_layout.addLayout(dataset_layout)

        # Fenstergröße sofort anpassen
        self.update_window_size()

    def remove_dataset_field(self, layout):
        """Entfernt ein Dataset-Feld und passt die Fenstergröße an."""
        while layout.count():
            widget = layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        self.datasets_layout.removeItem(layout)

        # Fenstergröße sofort anpassen
        self.update_window_size()

    def update_window_size(self):
        """Erzwingt die Anpassung der Fenstergröße."""
        self.datasets_widget.adjustSize()
        self.adjustSize()
        self.resize(self.sizeHint())

    def accept(self):
        """Speichert die Konfiguration in der Datei."""
        CONFIG["host"] = self.host_input.text()
        CONFIG["username"] = self.username_input.text()
        CONFIG["pool"] = self.pool_input.text()

        if self.password_input.text():
            CONFIG["password"] = encrypt_password(self.password_input.text())

        datasets = []
        for i in range(self.datasets_layout.count()):
            layout = self.datasets_layout.itemAt(i)
            if layout:
                name = layout.itemAt(1).widget().text()
                password = layout.itemAt(3).widget().text()
                datasets.append({
                    "name": name,
                    "password": encrypt_password(password) if password else None
                })
        CONFIG["datasets"] = datasets

        save_config()
        super().accept()
