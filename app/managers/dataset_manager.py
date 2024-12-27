from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt
from app.utils.api import fetch_datasets


class DatasetManager:
    def __init__(self, parent):
        self.parent = parent
        self.datasets = []  # To store dataset data
        self.outer_frame = None  # To hold the main widget for the tab
        self.layout = None  # To hold the layout

    def get_widget(self):
        """Creates and returns the datasets tab widget with a refresh button and dynamic content."""
        # Outer container for the tab content
        self.outer_frame = QFrame()
        self.outer_frame.setFrameShape(QFrame.Box)
        self.outer_frame.setFrameShadow(QFrame.Plain)
        self.outer_frame.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)

        # Layout for the outer frame
        self.layout = QVBoxLayout(self.outer_frame)
        self.layout.setAlignment(Qt.AlignTop)  # Align items to the top
        self.layout.setSpacing(5)  # Add spacing between rows

        # Add refresh button
        self.refresh_button = QPushButton("Refresh Datasets")
        self.refresh_button.clicked.connect(self.refresh_data)
        self.layout.addWidget(self.refresh_button)

        # Populate the layout with datasets
        self.refresh_data()

        return self.outer_frame

    def refresh_data(self):
        """Fetches and updates dataset information."""
        try:
            datasets = fetch_datasets()  # Replace with actual API fetch logic
            self.datasets = datasets
            self.update_layout()
        except Exception as e:
            self.parent.statusBar.showMessage(f"Error refreshing datasets: {str(e)}", 5000)

    def update_layout(self):
        """Updates the layout with dataset information."""
        # Clear existing rows while preserving the refresh button
        for i in reversed(range(1, self.layout.count())):  # Start at index 1 to skip the refresh button
            widget = self.layout.takeAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add header row
        self.layout.addWidget(self.create_header_row())

        # Add rows for each dataset
        for dataset in self.datasets:
            self.layout.addWidget(self.create_dataset_row(dataset))

    def create_header_row(self):
        """Creates a header row for the dataset columns."""
        header = QWidget()
        header_layout = QHBoxLayout(header)

        # Add header labels
        header_layout.addWidget(QLabel("Name"), alignment=Qt.AlignLeft)
        header_layout.addWidget(QLabel("State"), alignment=Qt.AlignCenter)
        header_layout.addWidget(QLabel("Usage"), alignment=Qt.AlignCenter)
        header_layout.addWidget(QLabel("Action"), alignment=Qt.AlignRight)

        # Ensure alignment and style
        header.setStyleSheet("font-weight: bold;")
        header_layout.setSpacing(15)

        return header

    def create_dataset_row(self, dataset):
        """Creates a single row for a dataset."""
        row = QWidget()
        row_layout = QHBoxLayout(row)

        # Dataset attributes
        name_label = QLabel(dataset.get("name", "Unknown"))
        state_label = QLabel("Locked 🔒" if dataset.get("keystatus") == "unavailable" else "Unlocked 🔓")
        usage_label = QLabel(f"{dataset.get('used_percent', 'N/A')}%")

        # Action button
        toggle_button = QPushButton("Un-/Lock")
        toggle_button.clicked.connect(lambda: self.toggle_state(dataset))

        # Add elements to the row layout
        row_layout.addWidget(name_label, alignment=Qt.AlignLeft)
        row_layout.addWidget(state_label, alignment=Qt.AlignCenter)
        row_layout.addWidget(usage_label, alignment=Qt.AlignCenter)
        row_layout.addWidget(toggle_button, alignment=Qt.AlignRight)

        # Set spacing and margins
        row_layout.setSpacing(15)
        row_layout.setContentsMargins(5, 5, 5, 5)

        return row

    def toggle_state(self, dataset):
        """Toggles the encryption state of a dataset."""
        from app.utils.api import lock_dataset, unlock_dataset
        try:
            if dataset.get("keystatus") == "unavailable":  # Locked, needs to be unlocked
                password, ok = self.parent.get_password(f"Unlock {dataset['name']}")
                if ok:
                    unlock_dataset(dataset["name"], password)
            else:  # Unlocked, needs to be locked
                lock_dataset(dataset["name"])

            self.refresh_data()
        except Exception as e:
            self.parent.statusBar.showMessage(f"Error toggling state for {dataset['name']}: {str(e)}", 5000)
