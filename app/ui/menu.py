from PyQt5.QtWidgets import QMenuBar, QAction
from app.utils.dark_mode import save_dark_mode_state, load_dark_mode_state


class MenuBuilder:
    def __init__(self, parent):
        """
        Initializes the MenuBuilder with a reference to the parent window.
        Args:
            parent (QMainWindow): The main window instance.
        """
        self.parent = parent

    def create_menu_bar(self):
        """
        Creates and returns a menu bar for the main window.
        """
        menu_bar = QMenuBar()

        # Settings Menu
        settings_menu = menu_bar.addMenu("Settings")
        self._add_settings_menu_items(settings_menu)

        # Logs Menu
        logs_menu = menu_bar.addMenu("Logs")
        self._add_logs_menu_items(logs_menu)

        # System Control Menu
        system_menu = menu_bar.addMenu("System Control")
        self._add_system_menu_items(system_menu)

        return menu_bar

    def _add_settings_menu_items(self, menu):
        """
        Adds settings-related items to the menu.
        Args:
            menu (QMenu): The settings menu.
        """
        # Configuration Action
        config_action = QAction("Configuration", self.parent)
        config_action.triggered.connect(self.parent.open_config_dialog)
        menu.addAction(config_action)

        # Reset Action
        reset_action = QAction("Reset App", self.parent)
        reset_action.triggered.connect(self.parent.reset_app)
        menu.addAction(reset_action)

        # Dark Mode Toggle
        dark_mode_action = QAction("Toggle Dark Mode", self.parent, checkable=True)
        dark_mode_action.setChecked(load_dark_mode_state())  # Initialize based on saved state
        dark_mode_action.triggered.connect(
            lambda: self._toggle_dark_mode(dark_mode_action.isChecked())
        )
        menu.addAction(dark_mode_action)

    def _add_logs_menu_items(self, menu):
        """
        Adds log-related items to the menu.
        Args:
            menu (QMenu): The logs menu.
        """
        app_log_action = QAction("Application Log", self.parent)
        app_log_action.triggered.connect(lambda: self.parent.view_log("app"))
        menu.addAction(app_log_action)

        server_log_action = QAction("Server Log", self.parent)
        server_log_action.triggered.connect(lambda: self.parent.view_log("server"))
        menu.addAction(server_log_action)

    def _add_system_menu_items(self, menu):
        """
        Adds system control items (reboot, shutdown) to the menu.
        Args:
            menu (QMenu): The system control menu.
        """
        # Reboot Action
        reboot_action = QAction("Reboot", self.parent)
        reboot_action.triggered.connect(self.parent.confirm_reboot)
        menu.addAction(reboot_action)

        # Shutdown Action
        shutdown_action = QAction("Shutdown", self.parent)
        shutdown_action.triggered.connect(self.parent.confirm_shutdown)
        menu.addAction(shutdown_action)

    def _toggle_dark_mode(self, enabled):
        """
        Toggles dark mode and saves the state.
        Args:
            enabled (bool): Whether dark mode is enabled.
        """
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
        if enabled:
            self.parent.setStyleSheet(dark_mode_stylesheet)
            self.parent.statusBar.showMessage("Dark mode enabled.", 5000)
        else:
            self.parent.setStyleSheet("")  # Reset to default
            self.parent.statusBar.showMessage("Dark mode disabled.", 5000)

        # Save the state
        save_dark_mode_state(enabled)
