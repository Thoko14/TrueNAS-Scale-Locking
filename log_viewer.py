from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout

class LogViewerDialog(QDialog):
    def __init__(self, title, log_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)

        self.log_file = log_file  # Path to the log file

        # Layout setup
        layout = QVBoxLayout(self)

        # Log viewer text area
        self.log_viewer = QTextEdit(self)
        self.log_viewer.setReadOnly(True)
        self.load_log_content()
        layout.addWidget(self.log_viewer)

        # Buttons for Clear Log and Close
        button_layout = QHBoxLayout()
        
        # Delete Log button
        self.delete_button = QPushButton("Delete Log", self)
        self.delete_button.clicked.connect(self.delete_log)
        button_layout.addWidget(self.delete_button)

        # Close button
        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def load_log_content(self):
        """Loads the content of the log file into the viewer."""
        try:
            with open(self.log_file, "r") as file:
                self.log_viewer.setPlainText(file.read())
        except FileNotFoundError:
            self.log_viewer.setPlainText("Log file not found.")
        except Exception as e:
            self.log_viewer.setPlainText(f"Error loading log file: {str(e)}")

    def delete_log(self):
        """Deletes the log file and clears the viewer."""
        import os
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
                self.log_viewer.setPlainText("Log file deleted.")
            else:
                self.log_viewer.setPlainText("Log file does not exist.")
        except Exception as e:
            self.log_viewer.setPlainText(f"Error deleting log file: {str(e)}")
