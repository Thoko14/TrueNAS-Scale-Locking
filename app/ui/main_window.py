import os
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QTabWidget, QWidget, QStatusBar, QMessageBox
)
from PyQt5.QtCore import QTimer, QThread
from app.ui.menu import MenuBuilder
from app.ui.dialogs.config_dialog import ConfigDialog
from app.ui.dialogs.log_viewer import LogViewerDialog
from app.ui.dialogs.rebootpopup import RebootPopup
from app.managers.dataset_manager import DatasetManager
from app.managers.disk_manager import DiskManager
from app.managers.performance_manager import PerformanceManager
from app.utils.app_logging import configure_logging
from app.utils.dark_mode import load_dark_mode_state
from app.utils.background_task import Worker
from app.utils.api import reboot_system, shutdown_system

class TrueNASManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker_thread = None  # Placeholder for the thread

        # Configure logging
        configure_logging()

        # Set up the main window
        self.setWindowTitle("TrueNAS Manager")
        self.setGeometry(100, 100, 900, 600)

        # Initialize menu bar
        self.init_menu_bar()

        # Initialize managers and UI
        self.init_managers()  # Initialize performance_manager and others
        self.init_ui()        # Initialize the UI (only after managers are set up)   
       
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # Apply dark mode if enabled
        if load_dark_mode_state():
            self.setStyleSheet(self.get_dark_mode_stylesheet())

        # Start periodic updates
        self.init_timers()

    def init_menu_bar(self):
        """Initializes the menu bar using MenuBuilder."""
        menu_builder = MenuBuilder(self)
        self.setMenuBar(menu_builder.create_menu_bar())

    def init_timers(self):
        """Initializes timers for periodic updates."""
        # Timer for performance updates
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.performance_manager.update_metrics)
        self.performance_timer.start(1000)

        # Timer for dataset and disk updates
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_data)
        self.refresh_timer.start(10000)

    def refresh_all_data(self):
        """Refreshes all data (datasets and disks)."""
        self.dataset_manager.refresh_data()
        self.disk_manager.refresh_data()

    def view_log(self, log_type):
        """Opens the log viewer for the specified log type."""
        log_path = os.path.join(os.getcwd(), f"{log_type}.log")
        log_dialog = LogViewerDialog(f"{log_type.capitalize()} Log", {"Log": log_path}, self)
        log_dialog.exec_()

    def open_config_dialog(self):
        """Opens the configuration dialog."""
        config_dialog = ConfigDialog(self)
        if config_dialog.exec_():
            self.statusBar.showMessage("Configuration updated.", 5000)

    def reset_app(self):
        """Resets the application."""
        reply = QMessageBox.warning(
            self,
            "Reset Application",
            "Are you sure you want to reset the application?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from app.utils.reset import reset_app
            reset_app()
            self.statusBar.showMessage("Application reset successfully.", 5000)

    
    def get_dark_mode_stylesheet(self):
        """Returns the dark mode stylesheet."""
        return """
        QMainWindow {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QLabel, QPushButton, QMenuBar, QMenu, QTabWidget, QTableWidget {
            color: #ffffff;
        }
        QTextEdit, QTableWidget {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #4d4d4d;
        }
        QPushButton {
            background-color: #4d4d4d;
            border: 1px solid #5d5d5d;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #5d5d5d;
        }
        QMenuBar {
            background-color: #3c3c3c;
        }
        QMenu {
            background-color: #3c3c3c;
            border: 1px solid #4d4d4d;
        }
        QTabWidget::pane {
            background-color: #2d2d2d;
            border: 1px solid #4d4d4d;
        }
        """
    
    def confirm_reboot(self):
        """Confirms and executes a system reboot."""
        reply = QMessageBox.warning(
            self,
            "Confirm Reboot",
            "Are you sure you want to reboot the system? The app will temporarily disconnect.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reboot_popup = RebootPopup(self)
            self.reboot_popup.label.setText("Rebooting. Please wait...")
            self.reboot_popup.show()

            # Start the reboot operation in a thread
            self.run_in_thread(reboot_system)

    def confirm_shutdown(self):
        """Confirms and executes a system shutdown."""
        reply = QMessageBox.warning(
            self,
            "Confirm Shutdown",
            "Are you sure you want to shut down the system? The app will close.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reboot_popup = RebootPopup(self)
            self.reboot_popup.label.setText("Shutting down. Please wait...")
            self.reboot_popup.show()

            # Start the shutdown operation in a thread
            self.run_in_thread(shutdown_system)

    def run_in_thread(self, function):
        """Runs a function in a separate thread."""
        self.worker_thread = QThread()
        self.worker = Worker(function)
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker.completed.connect(self.handle_task_completion)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        # Start the thread
        self.worker_thread.start()

    def handle_task_completion(self, success, result):
        """Handles the result of the background task."""
        self.worker_thread.quit()  # Stop the thread after task completion
        self.reboot_popup.close()  # Close the popup when done

        if success:
            if result == "shutdown":
                QMessageBox.information(
                    self,
                    "System Shutdown",
                    "The system has shut down. The app will now close.",
                )
                self.close()
            else:
                QMessageBox.information(
                    self,
                    "System Reboot",
                    "The system has rebooted and reconnected successfully."
                )
        else:
            QMessageBox.critical(
                self,
                "Operation Failed",
                f"An error occurred: {result}"
            )

    def init_managers(self):
        """Initializes the performance, dataset, and disk managers."""
        self.performance_manager = PerformanceManager(self)
        self.dataset_manager = DatasetManager(self)
        self.disk_manager = DiskManager(self)
    
    def init_ui(self):
        """Initializes the user interface."""
        # Set up main layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        # Add performance visualization from PerformanceManager
        self.main_layout.addWidget(self.performance_manager.get_widget())

        # Add tabs
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Add DiskManager and DatasetManager tabs
        self.tab_widget.addTab(self.disk_manager.get_widget(), "Disks")
        self.tab_widget.addTab(self.dataset_manager.get_widget(), "Datasets")