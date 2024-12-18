import sys
import logging
import time
from dark_mode_utils import save_dark_mode_state, load_dark_mode_state
from log_viewer import LogViewerDialog
from timestamp_utils import save_last_alert_check_time, load_last_alert_check_time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QHeaderView, QTableWidgetItem,
    QVBoxLayout, QLabel, QPushButton, QWidget, QTabWidget, QStatusBar, QInputDialog, QAction, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QGuiApplication
from config import load_config, save_config, decrypt_password
from ssh_commands import execute_ssh_command, fetch_datasets, fetch_smart_data, unlock_dataset, lock_dataset, reboot_system, shutdown_system, fetch_new_alerts, fetch_messages_log, fetch_alerts_log, fetch_combined_server_logs
from performance_visualisation import PerformanceVisualisation
from dialogs import ConfigDialog
from reset_utils import reset_app
from setup import SetupDialog
from datetime import datetime

import os
os.environ["PYTHONUTF8"] = "1"  # Force UTF-8 mode in Python


dark_mode_stylesheet = """
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
# Log file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_LOG_FILE = os.path.join(BASE_DIR, "app.log")

# Force log writing with handlers
logging.basicConfig(
    filename=APP_LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",  # Overwrite log file every time the app starts
    force=True     # Force reconfiguration if logging has already been set up
)

logging.info("Application started.")
print(f"Logging to: {APP_LOG_FILE}")

class TrueNASManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle("TrueNAS Dataset Manager")
        self.setGeometry(100, 100, 900, 600)

        # Center the main window
        self.center_window()

        # Initialize UI and Status Bar
        self.init_ui()
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")  # Initial message

        # Load Dark Mode State
        dark_mode_enabled = load_dark_mode_state()
        if dark_mode_enabled:
            self.setStyleSheet(dark_mode_stylesheet)
        
        # Periodic updates to Disks and Datasets (of needed)
        #self.timer = QTimer()
        #self.timer.timeout.connect(self.refresh_data)
        #self.timer.start(10000)  # Refresh every 10 seconds

        # Performance visualization update timer
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.performance_visualisation.update_metrics)
        self.perf_timer.start(1000)  # Update performance metrics every 1 second

        # Check for new alerts
        self.check_new_alerts()
       
        # Initial data load
        try:
            self.refresh_data()
        except Exception as e:
            self.statusBar.showMessage(f"Error: {str(e)}", 10000)

    def init_ui(self):
        """Initializes the UI."""
        self.init_menu_bar()  # Add the menu bar

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Performance Visualizations
        self.performance_visualisation = PerformanceVisualisation()
        perf_layout = QHBoxLayout()
        perf_layout.addWidget(self.performance_visualisation)
        self.performance_visualisation.setFixedHeight(300)  # Limit height of the visualizations
        main_layout.addLayout(perf_layout)

        # Create Tab Widget
        self.tab_widget = QTabWidget()

        # Disks Tab
        disks_tab = QWidget()
        disks_layout = QVBoxLayout(disks_tab)
        disks_layout.addWidget(QLabel("SMART Report:"))
        # Add Refresh Button
        refresh_smart_button = QPushButton("Refresh SMART Information")
        refresh_smart_button.clicked.connect(self.update_smart_table)  # Connect to SMART update
        disks_layout.addWidget(refresh_smart_button)
        self.smart_table = self.create_smart_table()
        disks_layout.addWidget(self.smart_table)
        self.tab_widget.addTab(disks_tab, "Disks")

        # Datasets Tab
        datasets_tab = QWidget()
        datasets_layout = QVBoxLayout(datasets_tab)
        datasets_layout.addWidget(QLabel("Dataset Management:"))
        # Add Refresh Button
        refresh_datasets_button = QPushButton("Refresh Dataset Information")
        refresh_datasets_button.clicked.connect(self.update_datasets_table)  # Connect to dataset update
        datasets_layout.addWidget(refresh_datasets_button)
        self.datasets_table = self.create_datasets_table()
        datasets_layout.addWidget(self.datasets_table)
        self.tab_widget.addTab(datasets_tab, "Datasets")

        # Add tabs to the main layout
        main_layout.addWidget(self.tab_widget)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def init_menu_bar(self):
        """Initializes the menu bar with reset, configuration, reboot, and shutdown options."""
        menu_bar = self.menuBar()

        # Settings Menu
        settings_menu = menu_bar.addMenu("Settings")
        
        config_action = QAction("Configuration", self)
        config_action.triggered.connect(self.open_config_dialog)
        settings_menu.addAction(config_action)

        reset_action = QAction("Reset App", self)
        reset_action.triggered.connect(self.confirm_reset)
        settings_menu.addAction(reset_action)

        # Toggle Dark Mode
        dark_mode_action = QAction("Toggle Dark Mode", self, checkable=True)
        dark_mode_action.setChecked(load_dark_mode_state())  # Set initial state
        dark_mode_action.triggered.connect(lambda: self.toggle_dark_mode(dark_mode_action.isChecked()))
        settings_menu.addAction(dark_mode_action)
        
        # System Control Menu
        system_menu = menu_bar.addMenu("System Control")
        
        reboot_action = QAction("Reboot", self)
        reboot_action.triggered.connect(self.confirm_reboot)
        system_menu.addAction(reboot_action)

        shutdown_action = QAction("Shutdown", self)
        shutdown_action.triggered.connect(self.confirm_shutdown)
        system_menu.addAction(shutdown_action)

        # Log Menu
        self.log_menu = menu_bar.addMenu("Logs")
        
        # App Log
        applog_action = QAction("App Log", self)
        applog_action.triggered.connect(self.view_applog)
        self.log_menu.addAction(applog_action)

        # Server Log
        serverlog_action = QAction("Server Log", self)
        serverlog_action.triggered.connect(self.view_serverlog)
        self.log_menu.addAction(serverlog_action)

    def toggle_dark_mode(self, enabled):
        """Toggles dark mode on or off and saves the state."""
        if enabled:
            self.setStyleSheet(dark_mode_stylesheet)
            self.statusBar.showMessage("Dark mode enabled.", 5000)
        else:
            self.setStyleSheet("")  # Reset to default
            self.statusBar.showMessage("Dark mode disabled.", 5000)
    
        # Save the dark mode state
        save_dark_mode_state(enabled)
    
    def add_log_alert_indicator(self):
        """Adds a red exclamation mark to the Logs menu if there are new alerts."""
        self.log_menu.setTitle("Logs ❗")  # Update menu title with an indicator
    
    def center_window(self):
        """Centers the main window on the screen."""
        screen_geometry = QGuiApplication.primaryScreen().geometry()  # Get the screen's geometry
        window_geometry = self.frameGeometry()  # Get the window's geometry
        center_point = screen_geometry.center()  # Find the screen's center
        window_geometry.moveCenter(center_point)  # Move the window's center to the screen's center
        self.move(window_geometry.topLeft())  # Move the window to its new position

    def check_new_alerts(self):
        """Checks for new alerts and updates the Log menu."""
        try:
            last_check_time = load_last_alert_check_time()
            new_alerts = fetch_new_alerts(last_check_time)
    
            if new_alerts.strip():  # If there are any new alerts
                self.add_log_alert_indicator()
                save_last_alert_check_time(time.time())  # Update last check time
        except Exception as e:
            self.statusBar.showMessage(f"Error checking for alerts: {str(e)}", 5000)
    
    def view_applog(self):
        """Opens the application log in a custom log viewer dialog."""
        try:
            # Define the absolute path to the app log
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            log_files = {"Application Log": os.path.join(BASE_DIR, "app.log")}  # Tabbed structure

            # Open the log viewer dialog with a single log
            log_dialog = LogViewerDialog("Application Log", log_files, self)
            log_dialog.exec_()
        except Exception as e:
            self.statusBar.showMessage(f"Error opening app log: {str(e)}", 10000)

    def view_serverlog(self):
        """Fetches and displays system messages and alerts logs in their respective tabs."""
        try:
            self.statusBar.showMessage("Fetching server logs...")

            # Fetch system messages
            system_messages = fetch_messages_log()
            safe_messages = system_messages.encode("utf-8", errors="replace").decode("utf-8", errors="replace")

            # Fetch alerts log
            alerts_log = fetch_alerts_log()
            safe_alerts = alerts_log.encode("utf-8", errors="replace").decode("utf-8", errors="replace")

            # Save logs to temporary files
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            system_log_file = os.path.join(BASE_DIR, "system_messages.log")
            alerts_log_file = os.path.join(BASE_DIR, "alerts.log")

            with open(system_log_file, "w", encoding="utf-8", errors="replace") as file:
                file.write(safe_messages)

            with open(alerts_log_file, "w", encoding="utf-8", errors="replace") as file:
                file.write(safe_alerts)

            # Check for new alerts
            last_check_time = load_last_alert_check_time()
            if last_check_time is None:
                last_check_time = datetime.min  # Ensure a valid default
            new_alerts = [line for line in safe_alerts.splitlines() if self.extract_timestamp(line) > last_check_time]

            if new_alerts:
                self.log_menu.setTitle("Logs ❗")  # Add red exclamation
            else:
                self.log_menu.setTitle("Logs")  # Reset menu title if no new alerts

            # Open the LogViewerDialog
            log_files = {
                "Alerts": alerts_log_file,
                "System Messages": system_log_file
            }

            log_dialog = LogViewerDialog("Server Logs", log_files, self)
            log_dialog.exec_()

            # After viewing, update the last check time
            save_last_alert_check_time(datetime.now())

            self.log_menu.setTitle("Logs")  # Clear indicator after viewing
            self.statusBar.showMessage("Server logs loaded successfully.", 5000)

        except Exception as e:
            self.statusBar.showMessage(f"Error fetching server logs: {str(e)}", 10000)

    def extract_timestamp(self, log_line):
        """Extracts a timestamp from a log line if present."""
        try:
            timestamp_str = log_line.split(" ")[0]  # Assume timestamp is at the start
            return datetime.fromisoformat(timestamp_str)
        except Exception:
            return datetime.min  # Return the minimum datetime if parsing fails

    def refresh_data(self):
        """Fetches and updates both tables."""
        self.statusBar.showMessage("Refreshing SMART and dataset information...")
        try:
            self.update_smart_table()
        except Exception as e:
            self.statusBar.showMessage(f"Error refreshing SMART data: {str(e)}", 10000)

        try:
            self.update_datasets_table()
        except Exception as e:
            self.statusBar.showMessage(f"Error refreshing dataset information: {str(e)}", 10000)

    def create_smart_table(self):
        """Creates the SMART table for disk information."""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Drive", "Temperature", "Health", "Actions"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def create_datasets_table(self):
        """Creates the datasets table."""
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Dataset", "Encryption State", "Action"])
        table.horizontalHeader().setStretchLastSection(True)
        return table

    def update_smart_table(self):
        """Fetches and updates the SMART table."""
        self.statusBar.showMessage("Refreshing SMART data...")
        try:
            smart_data = fetch_smart_data()
            self.smart_table.setRowCount(len(smart_data))
            for row, drive in enumerate(smart_data):
                self.smart_table.setItem(row, 0, QTableWidgetItem(drive["name"]))
                self.smart_table.setItem(row, 1, QTableWidgetItem(drive["temperature"]))
                self.smart_table.setItem(row, 2, QTableWidgetItem(drive["health"]))

                # Add details button
                details_button = QPushButton("Details")
                details_button.clicked.connect(lambda _, d=drive["name"]: self.show_smart_details(d))
                self.smart_table.setCellWidget(row, 3, details_button)
            self.statusBar.showMessage("SMART data refreshed successfully.", 5000)
        except Exception as e:
            self.statusBar.showMessage(f"Error refreshing SMART data: {str(e)}", 10000)

    def update_datasets_table(self):
        """Fetches and updates the datasets table."""
        try:
            datasets = fetch_datasets()  # Fetch dataset info from TrueNAS
            self.datasets_table.setColumnCount(5)
            self.datasets_table.setHorizontalHeaderLabels(
                ["Name", "Encryption State", "Snapshot Count", "Physical Used", "Actions"]
            )
            self.datasets_table.horizontalHeader().setSectionsMovable(True)  # Allow column reordering
            self.datasets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
            self.datasets_table.setRowCount(len(datasets))
            for row, dataset in enumerate(datasets):
                dataset_name = dataset["name"]
                key_status = dataset["keystatus"]
                encryption_state = "Locked 🔒" if key_status == "unavailable" else "Unlocked 🔓"
                encryption_color = "red" if key_status == "unavailable" else "green"
                snapshot_count = self.fetch_snapshot_count(dataset_name)
                physical_used = self.fetch_physical_used(dataset_name)
    
                # Column: Name
                self.datasets_table.setItem(row, 0, QTableWidgetItem(dataset_name))
    
                # Column: Encryption State with visual style
                state_label = QLabel(encryption_state)
                state_label.setStyleSheet(f"color: {encryption_color}; font-weight: bold;")
                self.datasets_table.setCellWidget(row, 1, state_label)
    
                # Column: Snapshot Count
                self.datasets_table.setItem(row, 2, QTableWidgetItem(snapshot_count))
    
                # Column: Physical Used
                self.datasets_table.setItem(row, 3, QTableWidgetItem(physical_used))
    
                # Column: Actions
                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(0, 0, 0, 0)
    
                # Encrypt/Decrypt Button
                toggle_button = QPushButton("Toggle")
                toggle_button.clicked.connect(lambda _, d=dataset_name, k=key_status: self.toggle_encryption_state(d, k))
                action_layout.addWidget(toggle_button)
    
                # Details Button
                details_button = QPushButton("Details")
                details_button.clicked.connect(lambda _, d=dataset_name: self.show_dataset_details(d))
                action_layout.addWidget(details_button)
    
                # Embed layout into the table cell
                container = QWidget()
                container.setLayout(action_layout)
                self.datasets_table.setCellWidget(row, 4, container)
    
            self.statusBar.showMessage("Dataset table updated successfully.", 3000)
        except Exception as e:
            self.statusBar.showMessage(f"Error updating dataset table: {str(e)}", 10000)

    def fetch_snapshot_count(self, dataset_name):
        """Fetches the number of snapshots for a dataset."""
        try:
            output = execute_ssh_command(f"zfs list -t snapshot -o name {dataset_name}")
            snapshots = output.strip().splitlines()
            return str(len(snapshots) - 1)  # Exclude the header
        except Exception:
            return "N/A"
    
    def fetch_physical_used(self, dataset_name):
        """Fetches the physical used space for a dataset."""
        try:
            output = execute_ssh_command(f"zfs get -H -o value physicalused {dataset_name}")
            return output.strip() or "N/A"
        except Exception:
            return "N/A"
    
    def show_dataset_details(self, dataset_name):
        """Displays additional dataset details in a dialog."""
        try:
            output = execute_ssh_command(f"zfs get all {dataset_name}")
            details_dialog = LogViewerDialog(f"Details for {dataset_name}", output, self)
            details_dialog.exec_()
        except Exception as e:
            self.statusBar.showMessage(f"Error fetching details: {str(e)}", 10000)


    def toggle_encryption_state(self, dataset_name, key_status):
        """Toggles the encryption state of a dataset."""
        self.statusBar.showMessage(f"Processing {dataset_name}...")
        try:
            if key_status == "unavailable":
                password, ok = QInputDialog.getText(self, "Password Required", f"Enter password for {dataset_name}:", QInputDialog.Password)
                if not ok or not password:
                    self.statusBar.showMessage("Unlock canceled.", 3000)
                    return
                unlock_dataset(dataset_name, password)
                self.statusBar.showMessage(f"Dataset {dataset_name} unlocked successfully.", 5000)
            else:
                lock_dataset(dataset_name)
                self.statusBar.showMessage(f"Dataset {dataset_name} locked successfully.", 5000)

            self.update_datasets_table()
        except Exception as e:
            self.statusBar.showMessage(f"Error processing {dataset_name}: {str(e)}", 10000)

    def show_dataset_details(self, dataset_name):
        """Displays additional dataset details in a dialog."""
        try:
            # Fetch all properties for the dataset
            output = execute_ssh_command(f"zfs get all {dataset_name}")
    
            # Use LogViewerDialog to display the details
            details_dialog = LogViewerDialog(f"Details for {dataset_name}", output, self)
            details_dialog.exec_()
        except Exception as e:
            self.statusBar.showMessage(f"Error fetching details: {str(e)}", 10000)
   
    def show_smart_details(self, drive_name):
        """Displays detailed SMART data for a specific drive."""
        QMessageBox.information(self, "SMART Details", f"Details for drive {drive_name}")

    def open_config_dialog(self):
        """Opens the configuration dialog."""
        config_dialog = ConfigDialog(self)
        if config_dialog.exec_():
            self.config = load_config()
            self.statusBar.showMessage("Configuration updated.", 10000)
    
    def confirm_reboot(self):
        """Confirms and reboots the system."""
        reply = QMessageBox.warning(
            self,
            "Reboot System",
            "Are you sure you want to reboot the TrueNAS server?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.statusBar.showMessage("Rebooting system...", 3000)
            try:
                reboot_system()
                self.statusBar.showMessage("System is rebooting.", 5000)
            except RuntimeError as e:
                self.statusBar.showMessage(f"Reboot failed: {str(e)}", 10000)

    def confirm_shutdown(self):
        """Confirms and shuts down the system."""
        reply = QMessageBox.warning(
            self,
            "Shutdown System",
            "Are you sure you want to shut down the TrueNAS server?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.statusBar.showMessage("Shutting down system...", 3000)
            try:
                shutdown_system()
                self.statusBar.showMessage("System is shutting down.", 5000)
            except RuntimeError as e:
                self.statusBar.showMessage(f"Shutdown failed: {str(e)}", 10000)
   
    def confirm_reset(self):
        """Confirms and resets the application."""
        reply = QMessageBox.warning(
            self,
            "Reset Application",
            "Are you sure you want to reset the application? All configurations will be deleted.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                reset_app()  # Ensure this function is implemented in reset_utils.py
                self.statusBar.showMessage("Application reset successfully.", 10000)
            except Exception as e:
                self.statusBar.showMessage(f"Error during reset: {str(e)}", 10000)



def initialize_app():
    """Checks if the configuration exists and is valid; launches setup if needed."""
    try:
        config = load_config()
        if not config.get("host") or not config.get("pool") or not config.get("datasets"):
            raise ValueError("Invalid or incomplete configuration.")
    except (FileNotFoundError, ValueError) as e:
        from setup import SetupDialog
        app = QApplication(sys.argv)
        QMessageBox.warning(None, "Configuration Missing", f"Error: {str(e)}\nThe setup dialog will now be launched.")
        setup_dialog = SetupDialog()
        if setup_dialog.exec_():
            print("Setup completed successfully. Application will start.")
        else:
            sys.exit("Setup canceled by the user. Exiting.")

def main():
    """Starts the application."""
    initialize_app()  # Ensure the configuration is valid or launch setup
    app = QApplication(sys.argv)
    main_window = TrueNASManager()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
