from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QWidget
from pyqtgraph import PlotWidget, mkPen

class PerformanceVisualisation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layouts for visualizations
        self.layout = QHBoxLayout(self)

        # CPU Plot
        self.cpu_plot = PlotWidget()
        self.cpu_plot.showGrid(x=True, y=True)
        self.cpu_data = [0] * 60
        self.cpu_curve = self.cpu_plot.plot(self.cpu_data, pen=mkPen('b', width=2))
        cpu_layout = QVBoxLayout()
        cpu_layout.addWidget(QLabel("CPU Usage"))
        cpu_layout.addWidget(self.cpu_plot)
        self.layout.addLayout(cpu_layout)

        # Disk I/O Plot
        self.disk_plot = PlotWidget()
        self.disk_plot.showGrid(x=True, y=True)
        self.disk_read_data = [0] * 60
        self.disk_write_data = [0] * 60
        self.disk_read_curve = self.disk_plot.plot(self.disk_read_data, pen=mkPen('g', width=2))
        self.disk_write_curve = self.disk_plot.plot(self.disk_write_data, pen=mkPen('r', width=2))
        disk_layout = QVBoxLayout()
        disk_layout.addWidget(QLabel("Disk I/O (Read/Write)"))
        disk_layout.addWidget(self.disk_plot)
        self.layout.addLayout(disk_layout)

        # Network Throughput Plot
        self.network_plot = PlotWidget()
        self.network_plot.showGrid(x=True, y=True)
        self.network_in_data = [0] * 60
        self.network_out_data = [0] * 60
        self.network_in_curve = self.network_plot.plot(self.network_in_data, pen=mkPen('c', width=2))
        self.network_out_curve = self.network_plot.plot(self.network_out_data, pen=mkPen('m', width=2))
        network_layout = QVBoxLayout()
        network_layout.addWidget(QLabel("Network Throughput (In/Out)"))
        network_layout.addWidget(self.network_plot)
        self.layout.addLayout(network_layout)

    def update(self, metrics):
        """Updates the visualization with new metrics."""
        # Update CPU Plot
        self.cpu_data = self.cpu_data[1:] + [metrics.get("cpu_load", 0)]
        self.cpu_curve.setData(self.cpu_data)

        # Update Disk I/O Plot
        self.disk_read_data = self.disk_read_data[1:] + [metrics.get("disk_read", 0)]
        self.disk_write_data = self.disk_write_data[1:] + [metrics.get("disk_write", 0)]
        self.disk_read_curve.setData(self.disk_read_data)
        self.disk_write_curve.setData(self.disk_write_data)

        # Update Network Plot
        self.network_in_data = self.network_in_data[1:] + [metrics.get("network_in", 0)]
        self.network_out_data = self.network_out_data[1:] + [metrics.get("network_out", 0)]
        self.network_in_curve.setData(self.network_in_data)
        self.network_out_curve.setData(self.network_out_data)
