import os
from PyQt6.QtCore import QRunnable, pyqtSignal, QObject
from core.config.img_conf import get_config as get_img_config
from core.config.login_data import delete_login
from core.providers.application.use_cases import ProviderGetPagesUseCase, ProviderDownloadUseCase
from core.slicer.application.use_cases import SlicerUseCase
from core.group_imgs.application.use_cases import GroupImgsUseCase
from GUI_qt.utils.config import get_config
from GUI_qt.utils.load_providers import base_path
import json


class DownloadWorkerSignals(QObject):
    progress_changed = pyqtSignal(int)
    download_error = pyqtSignal(str)
    color = pyqtSignal(str)
    name = pyqtSignal(str)


class DownloadWorker(QRunnable):
    def __init__(self, chapter, provider):
        super().__init__()
        self.chapter = chapter
        self.provider = provider
        self.signals = DownloadWorkerSignals()
        self.current_dir = os.path.join(base_path(), 'GUI_qt')
        self.assets = os.path.join(self.current_dir, 'assets')

    def run(self):
        try:
            img_conf = get_img_config()
            conf = get_config()
            
            try:
                pages = ProviderGetPagesUseCase(self.provider).execute(self.chapter)
            except Exception as e:
                self.signals.download_error.emit(f'{self.chapter.name} \n {self.chapter.number} \n Erro ao obter páginas: {str(e)}')
                return
            
            translations = {}

            with open(os.path.join(self.assets, 'translations.json'), 'r', encoding='utf-8') as file:
                translations = json.load(file)

            language = conf.lang
            if language not in translations:
                language = 'en'

            translation = translations[language]
            self.signals.name.emit(translation['downloading'])

            def set_progress_bar_style(color):
                self.signals.color.emit(f"""
                    QProgressBar {{
                        text-align: center;
                    }}
                    QProgressBar::chunk {{
                        background-color: {color};
                    }}
                    QProgressBar::text {{
                        color: #fff;
                        font-weight: bold;
                    }}
                """)

            set_progress_bar_style("#32CD32")
            
            def update_progress_bar(value):
                try:
                    self.signals.progress_changed.emit(int(value))
                except Exception as e:
                    print(f"Erro ao atualizar barra de progresso: {e}")

            try:
                ch = ProviderDownloadUseCase(self.provider).execute(pages=pages, fn=update_progress_bar)
            except Exception as e:
                self.signals.download_error.emit(f'{self.chapter.name} \n {self.chapter.number} \n Erro no download: {str(e)}')
                delete_login(self.provider.domain[0])
                return

            if img_conf.slice:
                try:
                    self.signals.name.emit(translation['slicing'])
                    self.signals.progress_changed.emit(0)
                    set_progress_bar_style("#0080FF")
                    ch = SlicerUseCase().execute(ch, update_progress_bar)
                except Exception as e:
                    self.signals.download_error.emit(f'{self.chapter.name} \n {self.chapter.number} \n Erro no slice: {str(e)}')
                    return

            if img_conf.group:
                try:
                    self.signals.name.emit(translation['grouping'])
                    self.signals.progress_changed.emit(0)
                    set_progress_bar_style("#FFA500")
                    GroupImgsUseCase().execute(ch, update_progress_bar)
                    self.signals.progress_changed.emit(100)
                except Exception as e:
                    self.signals.download_error.emit(f'{self.chapter.name} \n {self.chapter.number} \n Erro no agrupamento: {str(e)}')
                    return

        except Exception as e:
            try:
                set_progress_bar_style("red")
                self.signals.download_error.emit(f'{self.chapter.name} \n {self.chapter.number} \n Erro geral: {str(e)}')
                delete_login(self.provider.domain[0])
            except Exception as cleanup_error:
                print(f"Erro crítico no DownloadWorker: {e}")
                print(f"Erro no cleanup: {cleanup_error}")
                try:
                    self.signals.download_error.emit(f'Erro crítico: {str(e)}')
                except:
                    pass
