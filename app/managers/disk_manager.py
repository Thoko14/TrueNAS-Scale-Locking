from PyQt5.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt
from app.utils.api import fetch_smart_data


class DiskManager:
    def __init__(self, parent):
        self.parent = parent
        self.disks = []  # To store disk data
        self.outer_frame = None  # To hold the main widget for the tab
        self.layout = None  # To hold the layout

    def get_widget(self):
        """Creates and returns the disks tab widget with a refresh button and dynamic content."""
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
        self.refresh_button = QPushButton("Refresh Disks")
        self.refresh_button.clicked.connect(self.refresh_data)
        self.layout.addWidget(self.refresh_button)

        # Populate the layout with disks
        self.refresh_data()

        return self.outer_frame

    def refresh_data(self):
        """Fetches and updates disk information."""
        try:
            disks = fetch_smart_data()  # Replace with actual API fetch logic
            self.disks = disks
            self.update_layout()
        except Exception as e:
            self.parent.statusBar.showMessage(f"Error refreshing disks: {str(e)}", 5000)

    def update_layout(self):
        """Updates the layout with disk information."""
        # Clear existing rows while preserving the refresh button
        for i in reversed(range(1, self.layout.count())):  # Start at index 1 to skip the refresh button
            widget = self.layout.takeAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add header row
        self.layout.addWidget(self.create_header_row())

        # Add rows for each disk
        for disk in self.disks:
            self.layout.addWidget(self.create_disk_row(disk))

    def create_header_row(self):
        """Creates a header row for the disk columns."""
        header = QWidget()
        header_layout = QHBoxLayout(header)

        # Add header labels
        header_layout.addWidget(QLabel("Name"), alignment=Qt.AlignLeft)
        header_layout.addWidget(QLabel("Health"), alignment=Qt.AlignCenter)
        header_layout.addWidget(QLabel("Temperature"), alignment=Qt.AlignCenter)
        header_layout.addWidget(QLabel("Action"), alignment=Qt.AlignRight)

        # Ensure alignment and style
        header.setStyleSheet("font-weight: bold;")
        header_layout.setSpacing(15)

        return header

    def create_disk_row(self, disk):
        """Creates a single row for a disk."""
        row = QWidget()
        row_layout = QHBoxLayout(row)

        # Disk attributes
        name_label = QLabel(disk.get("name", "Unknown"))
        health_label = QLabel(disk.get("health", "Unknown"))
        temperature_label = QLabel(f"{disk.get('temperature', 'N/A')}°C")

        # Action button
        details_button = QPushButton("Details")
        details_button.clicked.connect(lambda: self.show_disk_details(disk))

        # Add elements to the row layout
        row_layout.addWidget(name_label, alignment=Qt.AlignLeft)
        row_layout.addWidget(health_label, alignment=Qt.AlignCenter)
        row_layout.addWidget(temperature_label, alignment=Qt.AlignCenter)
        row_layout.addWidget(details_button, alignment=Qt.AlignRight)

        # Set spacing and margins
        row_layout.setSpacing(15)
        row_layout.setContentsMargins(5, 5, 5, 5)

        return row

    def show_disk_details(self, disk):
        """Displays additional details about the selected disk."""
        QMessageBox.information(self.parent, "Disk Details", f"Details for disk: {disk.get('name')}")
