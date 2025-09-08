import os
from clipman import init
from PyQt6.QtCore import QThread, pyqtSignal
from GUI_qt.utils.git import update_providers, get_last_version
from GUI_qt.utils.version import version
from GUI_qt.windows.new_version import NewVersion


class UpdateThread(QThread):
    finished = pyqtSignal()

    def run(self):
        init()
        if os.environ.get('PYNEKOENV') != 'dev':
            update_providers()
            if version != get_last_version():
                NewVersion()
        self.finished.emit()
