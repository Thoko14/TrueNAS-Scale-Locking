import psutil
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QWidget
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot


class PerformanceVisualisation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        
        # CPU Utilization
        self.cpu_plot = PlotWidget(title="CPU Usage")
        self.cpu_plot.showGrid(x=True, y=True)
        self.cpu_data = [0] * 60
        self.cpu_curve = self.cpu_plot.plot(self.cpu_data, pen=pg.mkPen('b', width=2))
        self.layout.addWidget(QLabel("CPU Usage"))
        self.layout.addWidget(self.cpu_plot)

        # Memory Utilization
        self.memory_label = QLabel("Memory Usage: 0%")
        self.layout.addWidget(self.memory_label)

        # Disk I/O
        self.disk_plot = PlotWidget(title="Disk I/O")
        self.disk_plot.showGrid(x=True, y=True)
        self.disk_read_data = [0] * 60
        self.disk_write_data = [0] * 60
        self.disk_read_curve = self.disk_plot.plot(self.disk_read_data, pen=pg.mkPen('g', width=2))
        self.disk_write_curve = self.disk_plot.plot(self.disk_write_data, pen=pg.mkPen('r', width=2))
        self.layout.addWidget(QLabel("Disk I/O (Read/Write)"))
        self.layout.addWidget(self.disk_plot)

        # Network Throughput
        self.network_plot = PlotWidget(title="Network Throughput")
        self.network_plot.showGrid(x=True, y=True)
        self.network_in_data = [0] * 60
        self.network_out_data = [0] * 60
        self.network_in_curve = self.network_plot.plot(self.network_in_data, pen=pg.mkPen('c', width=2))
        self.network_out_curve = self.network_plot.plot(self.network_out_data, pen=pg.mkPen('m', width=2))
        self.layout.addWidget(QLabel("Network Throughput (In/Out)"))
        self.layout.addWidget(self.network_plot)

        self.setLayout(self.layout)

    def update_metrics(self):
        # CPU
        cpu_percent = psutil.cpu_percent()
        self.cpu_data = self.cpu_data[1:] + [cpu_percent]
        self.cpu_curve.setData(self.cpu_data)

        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        self.memory_label.setText(f"Memory Usage: {memory_percent}%")

        # Disk I/O
        disk_io = psutil.disk_io_counters()
        read_bytes = disk_io.read_bytes / (1024 * 1024)  # Convert to MB
        write_bytes = disk_io.write_bytes / (1024 * 1024)  # Convert to MB
        self.disk_read_data = self.disk_read_data[1:] + [read_bytes]
        self.disk_write_data = self.disk_write_data[1:] + [write_bytes]
        self.disk_read_curve.setData(self.disk_read_data)
        self.disk_write_curve.setData(self.disk_write_data)

        # Network
        network_io = psutil.net_io_counters()
        packets_sent = network_io.bytes_sent / (1024 * 1024)  # Convert to MB
        packets_received = network_io.bytes_recv / (1024 * 1024)  # Convert to MB
        self.network_in_data = self.network_in_data[1:] + [packets_received]
        self.network_out_data = self.network_out_data[1:] + [packets_sent]
        self.network_in_curve.setData(self.network_in_data)
        self.network_out_curve.setData(self.network_out_data)
