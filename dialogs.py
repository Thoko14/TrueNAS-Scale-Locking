from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QDialogButtonBox,
    QLabel, QPushButton, QMessageBox, QWidget, QSpacerItem, QSizePolicy
)
from config import CONFIG, save_config, encrypt_password


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konfiguration")
        self.setModal(True)

        # Hauptlayout
        self.main_layout = QVBoxLayout()

        # Dynamischer Bereich für Dataset-Felder (zuerst initialisieren!)
        self.datasets_widget = QWidget()
        self.datasets_layout = QVBoxLayout(self.datasets_widget)
        self.datasets_layout.setSpacing(10)
        self.datasets_layout.setContentsMargins(0, 0, 0, 0)

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

        # Dynamischer Bereich für Dataset-Felder hinzufügen
        self.main_layout.addWidget(self.datasets_widget)

        # Vorhandene Datasets laden
        for dataset in CONFIG["datasets"]:
            self.add_dataset_field(dataset["name"], dataset["password"])

        # + Button zum Hinzufügen neuer Datasets
        add_button = QPushButton("+ Dataset hinzufügen")
        add_button.clicked.connect(lambda: self.add_dataset_field("", ""))
        self.main_layout.addWidget(add_button)

        # Buttons
        buttons = QDialogButtonBox()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_all_fields)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        buttons.addButton(save_button, QDialogButtonBox.AcceptRole)
        buttons.addButton(clear_button, QDialogButtonBox.ActionRole)
        buttons.addButton(cancel_button, QDialogButtonBox.RejectRole)

        self.main_layout.addWidget(buttons)

        self.setLayout(self.main_layout)

        # Fenstergröße nach Layout-Initialisierung anpassen
        self.update_window_size()

    def add_dataset_field(self, name="", password=""):
        """Fügt ein neues Dataset-Feld hinzu."""
        dataset_layout = QHBoxLayout()

        # Felder für Dataset
        name_input = QLineEdit(name)
        password_input = QLineEdit(password)
        password_input.setEchoMode(QLineEdit.Password)

        # Löschen-Button
        delete_button = QPushButton("Löschen")
        delete_button.clicked.connect(lambda: self.confirm_and_remove_dataset_field(dataset_layout, name_input, password_input))

        # Hinzufügen der Widgets zum Layout
        dataset_layout.addWidget(QLabel("Name:"))
        dataset_layout.addWidget(name_input)
        dataset_layout.addWidget(QLabel("Passwort:"))
        dataset_layout.addWidget(password_input)
        dataset_layout.addWidget(delete_button)

        # Layout zum Hauptlayout hinzufügen
        self.datasets_layout.addLayout(dataset_layout)

        # Fenstergröße nur anpassen, wenn Resizing aktiviert ist
        self.update_window_size()

    def confirm_and_remove_dataset_field(self, layout, name_input, password_input):
        """Zeigt eine Warnung, wenn ein Dataset gelöscht wird, das nicht leer ist."""
        if name_input.text().strip() or password_input.text().strip():
            reply = QMessageBox.warning(
                self,
                "Löschen bestätigen",
                "Dieses Dataset enthält Daten. Sind Sie sicher, dass Sie es löschen möchten?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        self.remove_dataset_field(layout)

    def clear_all_fields(self):
        """Löscht alle Felderinhalte. Das letzte Dataset bleibt bestehen, aber dessen Inhalte werden geleert."""
        reply = QMessageBox.warning(
            self,
            "Alle Felder löschen",
            "Sind Sie sicher, dass Sie alle Felderinhalte löschen möchten? Dies kann nicht rückgängig gemacht werden.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        # Allgemeine Felder leeren
        self.host_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.pool_input.clear()

        # Datasets bearbeiten
        if self.datasets_layout.count() > 1:
            # Entferne alle Dataset-Felder außer dem letzten
            while self.datasets_layout.count() > 1:
                layout = self.datasets_layout.takeAt(0)
                if layout:
                    widget = layout.layout()
                    if widget:
                        for i in range(widget.count()):
                            child_widget = widget.itemAt(i).widget()
                            if child_widget:
                                child_widget.deleteLater()

        # Leere das letzte Dataset-Feld
        last_layout = self.datasets_layout.itemAt(0)
        if last_layout:
            widget = last_layout.layout()
            if widget:
                for i in range(widget.count()):
                    child_widget = widget.itemAt(i).widget()
                    if isinstance(child_widget, QLineEdit):  # Nur Textfelder leeren
                        child_widget.clear()

        # Fenstergröße anpassen
        self.update_window_size()


    def remove_dataset_field(self, layout):
        """Entfernt ein Dataset-Feld, sofern noch mindestens ein Feld übrig bleibt."""
        if self.datasets_layout.count() <= 1:
            QMessageBox.warning(
                self,
                "Löschen nicht möglich",
                "Es muss mindestens ein Dataset-Feld vorhanden sein."
            )
            return  
          
        """Entfernt ein Dataset-Feld und passt die Fenstergröße an."""
        while layout.count():
            widget = layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        self.datasets_layout.removeItem(layout)

        # Fenstergröße sofort anpassen
        self.update_window_size()

    def update_window_size(self):
        """Passt die Fensterhöhe dynamisch an, hält aber die Breite konstant."""
        self.datasets_widget.adjustSize()
        self.adjustSize()

        # Fixiere die Breite des Fensters
        current_width = self.width()
        new_height = self.sizeHint().height()
        self.resize(current_width, new_height)



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
