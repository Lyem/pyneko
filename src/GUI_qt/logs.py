import os
import sys
from PyQt6.QtGui import QIcon
from GUI_qt.load_providers import base_path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

current_dir = os.path.join(base_path(), 'GUI_qt')
assets = os.path.join(current_dir, 'assets')

class LogWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Logs")
        self.setGeometry(300, 300, 600, 400)
        self.setWindowIcon(QIcon(os.path.join(assets, 'icon.ico')))

        self.layout = QVBoxLayout(self)
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)

        self.layout.addWidget(self.log_output)

        sys.stdout = EmittingStream(textWritten=self.write_log)
        sys.stderr = EmittingStream(textWritten=self.write_log)

    def write_log(self, text):
        self.log_output.append(text)


class EmittingStream:
    def __init__(self, textWritten):
        self.textWritten = textWritten

    def write(self, text):
        if text.strip():
            self.textWritten(text)

    def flush(self):
        pass