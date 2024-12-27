from app.ui.performance_visualisation import PerformanceVisualisation
from app.utils.api import fetch_system_info, fetch_disk_stats, fetch_network_stats

class PerformanceManager:
    def __init__(self, parent=None):
        self.visualization = PerformanceVisualisation(parent)

    def get_widget(self):
        """Returns the visualization widget."""
        return self.visualization

    def update_metrics(self):
        """Fetches and updates performance metrics."""
        try:
            # Fetch System Info
            system_info = fetch_system_info()
            cpu_load = system_info.get("loadavg", [0])[0] if system_info else 0

            # Fetch Disk Stats
            disk_stats = fetch_disk_stats()
            disk_read = sum(disk.get("read_bytes", 0) for disk in disk_stats) / (1024 * 1024) if disk_stats else 0
            disk_write = sum(disk.get("write_bytes", 0) for disk in disk_stats) / (1024 * 1024) if disk_stats else 0

            # Fetch Network Stats
            network_stats = fetch_network_stats()
            network_in = sum(interface.get("received_bytes", 0) for interface in network_stats) / (1024 * 1024) if network_stats else 0
            network_out = sum(interface.get("sent_bytes", 0) for interface in network_stats) / (1024 * 1024) if network_stats else 0

            # Update Visualization
            self.visualization.update({
                "cpu_load": cpu_load,
                "disk_read": disk_read,
                "disk_write": disk_write,
                "network_in": network_in,
                "network_out": network_out
            })

        except Exception as e:
            print(f"Error updating performance metrics: {e}")
