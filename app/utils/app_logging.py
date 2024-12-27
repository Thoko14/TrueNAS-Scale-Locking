import logging
import os

def configure_logging():
    """
    Configures logging for the application.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_FILE = os.path.join(BASE_DIR, "../../logs/app.log")

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
        force=True  # Ensure this config applies even if logging is already configured
    )

    logging.info("Application started.")
    print(f"Logging to: {LOG_FILE}")
