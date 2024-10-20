import os
import sys
import json
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QLocale
from GUI_qt.load_providers import base_path
from GUI_qt.config import get_config, update_lang
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

def base():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return base_path()
current_dir = os.path.join(base(), 'GUI_qt')
assets = os.path.join(current_dir, 'assets')

class LoadingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyNeko")
        self.setFixedSize(300, 100)
        self.setWindowIcon(QIcon(os.path.join(assets, 'icon.ico')))

        translations = {}
        with open(os.path.join(assets, 'translations.json'), 'r', encoding='utf-8') as file:
            translations = json.load(file)

        config = get_config()
        if not config:
            language = QLocale.system().name()
            update_lang(language)
        else:
            language = config.lang
        if language not in translations:
            language = 'en'
        
        translation = translations[language]
        
        layout = QVBoxLayout()
        self.label = QLabel(translation['updates'])
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)