from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt


class RebootPopup(QDialog):
    """
    A popup dialog to show reboot/reconnecting progress.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Reboot")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setGeometry(400, 300, 300, 150)

        # Layout
        self.layout = QVBoxLayout(self)
        
        # Message Label
        self.label = QLabel("Rebooting the system and reconnecting. Please wait...")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        
        # Progress Bar (optional)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.layout.addWidget(self.progress_bar)
