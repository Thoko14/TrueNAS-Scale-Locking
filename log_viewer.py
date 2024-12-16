from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton

class LogViewerDialog(QDialog):
    def __init__(self, title, log_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Scrollable text area
        self.log_viewer = QTextEdit(self)
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setPlainText(log_content)
        layout.addWidget(self.log_viewer)

        # Close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
