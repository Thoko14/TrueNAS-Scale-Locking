import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QHeaderView, QTableWidgetItem,
    QVBoxLayout, QLabel, QPushButton, QWidget, QTabWidget, QStatusBar, QInputDialog, QAction, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QGuiApplication
from config import load_config, save_config, decrypt_password
from ssh_commands import execute_ssh_command, fetch_datasets, fetch_smart_data, unlock_dataset, lock_dataset, reboot_system, shutdown_system
from performance_visualisation import PerformanceVisualisation
from dialogs import ConfigDialog
from reset_utils import reset_app
from setup import SetupDialog

# Configure logging
logging.basicConfig(
    filename="app.log",  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s"  # Log format
)

# Example usage
logging.info("Application started.")

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

        # Periodic updates to Disks and Datasets (of needed)
        #self.timer = QTimer()
        #self.timer.timeout.connect(self.refresh_data)
        #self.timer.start(10000)  # Refresh every 10 seconds

        # Performance visualization update timer
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.performance_visualisation.update_metrics)
        self.perf_timer.start(1000)  # Update performance metrics every 1 second

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

        # System Control Menu
        system_menu = menu_bar.addMenu("System Control")
        
        reboot_action = QAction("Reboot", self)
        reboot_action.triggered.connect(self.confirm_reboot)
        system_menu.addAction(reboot_action)

        shutdown_action = QAction("Shutdown", self)
        shutdown_action.triggered.connect(self.confirm_shutdown)
        system_menu.addAction(shutdown_action)

        # Log Menu
        log_menu = menu_bar.addMenu("Logs")
        
        # App Log
        applog_action = QAction("App Log", self)
        applog_action.triggered.connect(self.view_applog)
        log_menu.addAction(applog_action)
        
        # Server Log
        serverlog_action = QAction("Server Log", self)
        serverlog_action.triggered.connect(self.view_serverlog)
        log_menu.addAction(serverlog_action)


    def center_window(self):
        """Centers the main window on the screen."""
        screen_geometry = QGuiApplication.primaryScreen().geometry()  # Get the screen's geometry
        window_geometry = self.frameGeometry()  # Get the window's geometry
        center_point = screen_geometry.center()  # Find the screen's center
        window_geometry.moveCenter(center_point)  # Move the window's center to the screen's center
        self.move(window_geometry.topLeft())  # Move the window to its new position

    def view_applog(self):
        """Opens the application log in a text viewer."""
        try:
            with open("app.log", "r") as log_file:
                log_contents = log_file.read()
    
            # Display the log in a QMessageBox
            log_dialog = QMessageBox(self)
            log_dialog.setWindowTitle("Application Log")
            log_dialog.setText(log_contents)
            log_dialog.setStandardButtons(QMessageBox.Ok)
            log_dialog.exec_()
        except FileNotFoundError:
            self.statusBar.showMessage("App log file not found.", 5000)
        except Exception as e:
            self.statusBar.showMessage(f"Error opening app log: {str(e)}", 10000)
    
    def view_serverlog(self):
    """Fetches and displays the server log."""
    try:
        log_contents = fetch_server_log("/var/log/messages")  # Replace with desired log path

        # Display the log in a QMessageBox
        log_dialog = QMessageBox(self)
        log_dialog.setWindowTitle("Server Log")
        log_dialog.setText(log_contents)
        log_dialog.setStandardButtons(QMessageBox.Ok)
        log_dialog.exec_()
    except Exception as e:
        self.statusBar.showMessage(f"Error fetching server log: {str(e)}", 10000)
    
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
        self.statusBar.showMessage("Refreshing dataset information...")
        try:
            datasets = fetch_datasets()
            self.datasets_table.setRowCount(len(datasets))
            for row, dataset in enumerate(datasets):
                dataset_name = dataset["name"]
                key_status = dataset["keystatus"]

                self.datasets_table.setItem(row, 0, QTableWidgetItem(dataset_name))

                # Encryption State
                state_label = QLabel("Locked 🔒" if key_status == "unavailable" else "Unlocked 🔓")
                state_label.setStyleSheet("color: red;" if key_status == "unavailable" else "color: green;")
                self.datasets_table.setCellWidget(row, 1, state_label)

                # Action Button
                action_button = QPushButton("Unlock" if key_status == "unavailable" else "Lock")
                action_button.clicked.connect(lambda _, d=dataset_name, k=key_status: self.toggle_encryption_state(d, k))
                self.datasets_table.setCellWidget(row, 2, action_button)
            self.statusBar.showMessage("Dataset information refreshed successfully.", 5000)
        except Exception as e:
            self.statusBar.showMessage(f"Error refreshing dataset information: {str(e)}", 10000)

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
