# app/utils/system_controls.py

import logging
from PyQt5.QtWidgets import (
    QAction
)

def reboot_system():
    """Executes the system reboot."""
    try:
        # Add actual reboot logic here, e.g., via API or system command
        logging.info("System reboot initiated.")
        print("System reboot initiated.")  # Placeholder for actual logic
    except Exception as e:
        logging.error(f"Failed to reboot system: {e}")
        raise RuntimeError(f"Failed to reboot system: {e}")


def shutdown_system():
    """Executes the system shutdown."""
    try:
        # Add actual shutdown logic here, e.g., via API or system command
        logging.info("System shutdown initiated.")
        print("System shutdown initiated.")  # Placeholder for actual logic
    except Exception as e:
        logging.error(f"Failed to shut down system: {e}")
        raise RuntimeError(f"Failed to shut down system: {e}")

def _add_system_menu_items(self, menu):
    """Adds system control items (reboot, shutdown) to the menu."""
    # Reboot Action
    reboot_action = QAction("Reboot", self.parent)
    reboot_action.triggered.connect(self.parent.confirm_reboot)
    menu.addAction(reboot_action)

    # Shutdown Action
    shutdown_action = QAction("Shutdown", self.parent)
    shutdown_action.triggered.connect(self.parent.confirm_shutdown)
    menu.addAction(shutdown_action)
