import os
from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QWidget
)

class LogViewerDialog(QDialog):
    def __init__(self, title, log_files, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)
        self.log_files = log_files  # Dictionary of log types and their file paths

        # Layout setup
        main_layout = QVBoxLayout(self)

        # Tab widget to hold logs for different categories
        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        # Add tabs for each log file, ensuring Alerts is the first tab
        self.tabs = {}
        sorted_log_files = {k: log_files[k] for k in sorted(log_files, key=lambda x: x != "Alerts")}
        for log_type, log_file in sorted_log_files.items():
            self.add_log_tab(log_type, log_file)

        # Buttons: Refresh All, Close
        button_layout = QHBoxLayout()

        # Refresh All button
        self.refresh_button = QPushButton("Refresh All", self)
        self.refresh_button.clicked.connect(self.refresh_all_logs)
        button_layout.addWidget(self.refresh_button)

        # Close button
        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

    def add_log_tab(self, log_type, log_file):
        """Adds a new tab for the specified log type."""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # Log viewer text area
        log_viewer = QTextEdit(tab)
        log_viewer.setReadOnly(True)
        tab_layout.addWidget(log_viewer)

        # Store references for later use
        self.tabs[log_type] = {
            "log_file": log_file,
            "log_viewer": log_viewer
        }

        # Load initial log content
        self.load_log_content(log_type)

        # Add tab to the widget
        self.tab_widget.addTab(tab, log_type)

    def load_log_content(self, log_type):
        """Loads the content of the log file into the corresponding viewer."""
        tab_data = self.tabs.get(log_type)
        if not tab_data:
            return

        log_file = tab_data["log_file"]
        log_viewer = tab_data["log_viewer"]

        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8", errors="replace") as file:
                    content = file.read()
                log_viewer.setPlainText(content)
            except Exception as e:
                log_viewer.setPlainText(f"Error loading log file: {str(e)}")
        else:
            log_viewer.setPlainText("Log file not found.")

    def refresh_all_logs(self):
        """Refreshes all logs in all tabs."""
        for log_type in self.tabs.keys():
            self.load_log_content(log_type)