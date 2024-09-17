import os
import sys
import webbrowser
from PyQt6.QtGui import QIcon
from GUI_qt.git import get_last_version
from GUI_qt.load_providers import base_path
from PyQt6.QtWidgets import QMessageBox, QMainWindow

current_dir = os.path.join(base_path(), 'GUI_qt')
assets = os.path.join(current_dir, 'assets')

class NewVersion(QMainWindow):
    def __init__(self):
        super().__init__()

        self.show_message_box()

    def show_message_box(self):
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(os.path.join(assets, 'icon.ico')))
        msg_box.setWindowTitle("Nova versão")
        msg_box.setText("Deseja baixar a nova versão disponivel?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        msg_box.button(QMessageBox.StandardButton.Ok).clicked.connect(self.open_website)
        msg_box.button(QMessageBox.StandardButton.Cancel).clicked.connect(self.close_application)
        
        msg_box.exec()

    def open_website(self):
        version = get_last_version()
        webbrowser.open(f'https://github.com/Lyem/pyneko/releases/tag/v{version}')
        sys.exit()
    
    def close_application(self):
        sys.exit()

