from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QWidget
import psutil
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import time

class PerformanceVisualisation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout()  # Main vertical layout

        # Top section for CPU, Disk I/O, and Network Throughput visualizations
        self.visualization_layout = QHBoxLayout()

        # CPU Utilization
        self.cpu_plot = PlotWidget()
        self.cpu_plot.showGrid(x=True, y=True)
        self.cpu_data = [0] * 60
        self.cpu_curve = self.cpu_plot.plot(self.cpu_data, pen=pg.mkPen('b', width=2))
        cpu_layout = QVBoxLayout()
        cpu_layout.addWidget(QLabel("CPU Usage"))
        cpu_layout.addWidget(self.cpu_plot)
        self.visualization_layout.addLayout(cpu_layout)

        # Disk I/O
        self.disk_plot = PlotWidget()
        self.disk_plot.showGrid(x=True, y=True)
        self.disk_read_data = [0] * 60
        self.disk_write_data = [0] * 60
        self.disk_read_curve = self.disk_plot.plot(self.disk_read_data, pen=pg.mkPen('g', width=2))
        self.disk_write_curve = self.disk_plot.plot(self.disk_write_data, pen=pg.mkPen('r', width=2))
        disk_layout = QVBoxLayout()
        disk_layout.addWidget(QLabel("Disk I/O (Read/Write)"))
        disk_layout.addWidget(self.disk_plot)
        self.visualization_layout.addLayout(disk_layout)

        # Network Throughput
        self.network_plot = PlotWidget()
        self.network_plot.showGrid(x=True, y=True)
        self.network_in_data = [0] * 60
        self.network_out_data = [0] * 60
        self.network_in_curve = self.network_plot.plot(self.network_in_data, pen=pg.mkPen('c', width=2))
        self.network_out_curve = self.network_plot.plot(self.network_out_data, pen=pg.mkPen('m', width=2))
        network_layout = QVBoxLayout()
        network_layout.addWidget(QLabel("Network Throughput (In/Out)"))
        network_layout.addWidget(self.network_plot)
        self.visualization_layout.addLayout(network_layout)

        # Add visualization layout to the main layout
        self.main_layout.addLayout(self.visualization_layout)

        # Memory Utilization (below the graphs)
        self.memory_label = QLabel("Memory Usage: 0%")
        self.main_layout.addWidget(self.memory_label)

        self.setLayout(self.main_layout)

        # Initialize previous metrics for delta calculations
        self.previous_disk_io = psutil.disk_io_counters()
        self.previous_network_io = psutil.net_io_counters()
        self.previous_time = time.time()

    def update_metrics(self):
        current_time = time.time()
        elapsed_time = current_time - self.previous_time
        self.previous_time = current_time

        # CPU
        cpu_percent = psutil.cpu_percent()
        self.cpu_data = self.cpu_data[1:] + [cpu_percent]
        self.cpu_curve.setData(self.cpu_data)

        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        self.memory_label.setText(f"Memory Usage: {memory_percent}%")

        # Disk I/O
        current_disk_io = psutil.disk_io_counters()
        read_delta = (current_disk_io.read_bytes - self.previous_disk_io.read_bytes) / (1024 * 1024)  # Convert to MB
        write_delta = (current_disk_io.write_bytes - self.previous_disk_io.write_bytes) / (1024 * 1024)  # Convert to MB
        self.previous_disk_io = current_disk_io

        self.disk_read_data = self.disk_read_data[1:] + [read_delta / elapsed_time]
        self.disk_write_data = self.disk_write_data[1:] + [write_delta / elapsed_time]
        self.disk_read_curve.setData(self.disk_read_data)
        self.disk_write_curve.setData(self.disk_write_data)

        # Network
        current_network_io = psutil.net_io_counters()
        in_delta = (current_network_io.bytes_recv - self.previous_network_io.bytes_recv) / (1024 * 1024)  # Convert to MB
        out_delta = (current_network_io.bytes_sent - self.previous_network_io.bytes_sent) / (1024 * 1024)  # Convert to MB
        self.previous_network_io = current_network_io

        self.network_in_data = self.network_in_data[1:] + [in_delta / elapsed_time]
        self.network_out_data = self.network_out_data[1:] + [out_delta / elapsed_time]
        self.network_in_curve.setData(self.network_in_data)
        self.network_out_curve.setData(self.network_out_data)