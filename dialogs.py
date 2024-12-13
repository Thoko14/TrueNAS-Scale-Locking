from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QDialogButtonBox,
    QLabel, QPushButton, QMessageBox, QWidget, QSpacerItem, QSizePolicy
)
from config import load_config, save_config, encrypt_password


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.config = load_config()  # Load the most recent configuration
        self.setModal(True)

        # Main layout
        self.main_layout = QVBoxLayout()

        # Dynamic area for dataset fields (initialized first)
        self.datasets_widget = QWidget()
        self.datasets_layout = QVBoxLayout(self.datasets_widget)
        self.datasets_layout.setSpacing(10)
        self.datasets_layout.setContentsMargins(0, 0, 0, 0)

        # General settings in 2 columns
        general_layout = QHBoxLayout()

        # Left column: Host-IP and Username
        left_layout = QVBoxLayout()
        self.host_input = QLineEdit(self.config["host"])
        self.username_input = QLineEdit(self.config["username"])
        left_layout.addWidget(QLabel("Host-IP:"))
        left_layout.addWidget(self.host_input)
        left_layout.addWidget(QLabel("Username:"))
        left_layout.addWidget(self.username_input)

        # Right column: Password and Pool-Name
        right_layout = QVBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.pool_input = QLineEdit(self.config["pool"])
        right_layout.addWidget(QLabel("Password:"))
        right_layout.addWidget(self.password_input)
        right_layout.addWidget(QLabel("Pool-Name:"))
        right_layout.addWidget(self.pool_input)

        # Join columns
        general_layout.addLayout(left_layout)
        general_layout.addSpacing(30)  # Space between columns
        general_layout.addLayout(right_layout)
        self.main_layout.addLayout(general_layout)

        # Fixed label for datasets
        label_layout = QHBoxLayout()
        self.datasets_label = QLabel("Datasets:")
        label_layout.addWidget(self.datasets_label)
        label_layout.addSpacerItem(QSpacerItem(40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addLayout(label_layout)

        # Dynamic area for dataset fields
        self.main_layout.addWidget(self.datasets_widget)

        # Load existing datasets or add empty fields
        if not self.config.get("datasets"):
            self.add_dataset_field("", "")
        else:
            for dataset in self.config["datasets"]:
                self.add_dataset_field(dataset["name"], dataset["password"])

        # + Button to add a new dataset
        add_button = QPushButton("+ Add dataset")
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

        # Adjust window size after layout initialization
        self.update_window_size()

    def add_dataset_field(self, name="", password=""):
        """Add a new Dataset-Field."""
        dataset_layout = QHBoxLayout()

        # Fields for a Dataset
        name_input = QLineEdit(name)
        password_input = QLineEdit(password)
        password_input.setEchoMode(QLineEdit.Password)

        # Delete-Button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.confirm_and_remove_dataset_field(dataset_layout, name_input, password_input))

        # Add Widgets to Layout
        dataset_layout.addWidget(QLabel("Name:"))
        dataset_layout.addWidget(name_input)
        dataset_layout.addWidget(QLabel("Password:"))
        dataset_layout.addWidget(password_input)
        dataset_layout.addWidget(delete_button)

        # Add Layout to Main Layout
        self.datasets_layout.addLayout(dataset_layout)

        # Adjust window size
        self.update_window_size()

    def confirm_and_remove_dataset_field(self, layout, name_input, password_input):
        """Displays a warning when deleting a dataset that is not empty."""
        if name_input.text().strip() or password_input.text().strip():
            reply = QMessageBox.warning(
                self,
                "Confirm Deletion",
                "This dataset contains data. Are you sure you want to delete it?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        self.remove_dataset_field(layout)

    def clear_all_fields(self):
        """Clears all field contents. The last dataset remains, but its contents are cleared."""
        reply = QMessageBox.warning(
            self,
            "Clear All Fields",
            "Are you sure you want to clear all fields? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        # Clear general fields
        self.host_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.pool_input.clear()

        # Handle datasets
        if self.datasets_layout.count() > 1:
            # Remove all dataset fields except the last
            while self.datasets_layout.count() > 1:
                layout = self.datasets_layout.takeAt(0)
                if layout:
                    widget = layout.layout()
                    if widget:
                        for i in range(widget.count()):
                            child_widget = widget.itemAt(i).widget()
                            if child_widget:
                                child_widget.deleteLater()

        # Clear the last dataset field
        last_layout = self.datasets_layout.itemAt(0)
        if last_layout:
            widget = last_layout.layout()
            if widget:
                for i in range(widget.count()):
                    child_widget = widget.itemAt(i).widget()
                    if isinstance(child_widget, QLineEdit):  # Only clear text fields
                        child_widget.clear()

        # Adjust window size
        self.update_window_size()

    def remove_dataset_field(self, layout):
        """Removes a dataset field if at least one field remains."""
        if self.datasets_layout.count() <= 1:
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "At least one dataset field must remain."
            )
            return

        # Remove the dataset field and adjust the window size
        while layout.count():
            widget = layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        self.datasets_layout.removeItem(layout)

        # Adjust window size immediately
        self.update_window_size()

    def update_window_size(self):
        """Dynamically adjusts the window height while keeping the width constant."""
        self.datasets_widget.adjustSize()
        self.adjustSize()

        # Fix the window width
        current_width = self.width()
        new_height = self.sizeHint().height()
        self.resize(current_width, new_height)

    def accept(self):
        """Saves the configuration to the file."""
        self.config["host"] = self.host_input.text()
        self.config["username"] = self.username_input.text()
        self.config["pool"] = self.pool_input.text()

        if self.password_input.text():
            self.config["password"] = encrypt_password(self.password_input.text())

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
        self.config["datasets"] = datasets

        save_config(self.config)
        super().accept()
