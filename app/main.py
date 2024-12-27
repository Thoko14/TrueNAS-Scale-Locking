# Main application entry
import sys
import os 

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import QApplication
from app.utils.config import load_config
from app.ui.main_window import TrueNASManager
from app.ui.dialogs.setup_dialog import SetupDialog
from app.utils.app_logging import configure_logging




def initialize_app():
    """
    Ensures the configuration exists and is valid. Launches setup if needed.
    """
    try:
        # Try loading the configuration
        config = load_config()
        if not config.get("host") or not config.get("api_key"):
            raise ValueError("Invalid or incomplete configuration.")
    except (FileNotFoundError, ValueError) as e:
        app = QApplication(sys.argv)
        from PyQt5.QtWidgets import QMessageBox

        QMessageBox.warning(None, "Configuration Missing", f"Error: {str(e)}\nThe setup dialog will now be launched.")
        setup_dialog = SetupDialog()
        if not setup_dialog.exec_():  # If setup is canceled
            sys.exit("Setup canceled by the user. Exiting.")

def main():
    """
    Starts the TrueNAS Manager application.
    """
    configure_logging()  # Set up logging
    initialize_app()     # Ensure valid configuration

    app = QApplication(sys.argv)
    main_window = TrueNASManager()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
