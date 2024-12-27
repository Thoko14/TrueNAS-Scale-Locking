from PyQt5.QtCore import QObject, QThread, pyqtSignal


class Worker(QObject):
    """
    A worker class to execute a function in a separate thread and emit signals on completion.
    """
    completed = pyqtSignal(bool, object)  # Emits success status and result

    def __init__(self, function):
        """
        Initializes the worker.

        Args:
            function (callable): The function to execute in the background.
        """
        super().__init__()
        self.function = function

    def run(self):
        """Executes the task."""
        try:
            result = self.function()
            self.completed.emit(True, result)
        except Exception as e:
            self.completed.emit(False, str(e))
