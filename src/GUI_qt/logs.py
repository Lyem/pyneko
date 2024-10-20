import os
import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QTextCursor
from GUI_qt.load_providers import base_path
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton

current_dir = os.path.join(base_path(), 'GUI_qt')
assets = os.path.join(current_dir, 'assets')

class LogEmitter(QObject):
    log_signal = pyqtSignal(str)

class LogThread(QThread):
    def __init__(self, emitter):
        super().__init__()
        self.emitter = emitter

    def run(self):
        sys.stdout = EmittingStream(self.emitter.log_signal)
        sys.stderr = EmittingStream(self.emitter.log_signal)

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

        self.emitter = LogEmitter()
        self.emitter.log_signal.connect(self.write_log)

        self.log_thread = LogThread(self.emitter)
        self.log_thread.start()

        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        self.layout.addWidget(self.clear_button)

        self.scroll_at_bottom = True
        self.log_output.verticalScrollBar().valueChanged.connect(self.check_scroll_position)
    
    def clear_logs(self):
        self.log_output.clear()

    def write_log(self, text: str):
        if "[no-render]" in text:
            self.log_output.append(text)
        else:
            text = text + '<br>'
            self.log_output.insertHtml(text)
        if self.scroll_at_bottom:
            self.log_output.moveCursor(QTextCursor.MoveOperation.End)
    
    def check_scroll_position(self):
        max_value = self.log_output.verticalScrollBar().maximum()
        current_value = self.log_output.verticalScrollBar().value()
        
        margin = 10
        
        self.scroll_at_bottom = (current_value >= max_value - margin)

class EmittingStream:
    def __init__(self, signal):
        self.signal = signal

    def write(self, text):
        if text.strip():
            self.signal.emit(text)

    def flush(self):
        pass