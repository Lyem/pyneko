from PyQt6.QtCore import QRunnable, pyqtSignal, QObject
from core.config.login_data import delete_login
from core.providers.application.use_cases import ProviderMangaUseCase, ProviderGetChaptersUseCase, ProviderLoginUseCase


class MangaTaskSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)


class MangaTask(QRunnable):
    def __init__(self, provider, link):
        super().__init__()
        self.provider = provider
        self.link = link
        self.signal = MangaTaskSignals()

    def run(self):
        try:
            if self.provider.has_login:
                try:
                    ProviderLoginUseCase(self.provider).execute()
                except Exception as e:
                    self.signal.error.emit(f"Erro no login: {str(e)}")
                    return
                    
            try:
                manga = ProviderMangaUseCase(self.provider).execute(self.link)
                self.signal.finished.emit(manga)
            except Exception as e:
                self.signal.error.emit(f"Erro ao obter manga: {str(e)}")
                delete_login(self.provider.domain[0])
                
        except Exception as e:
            try:
                delete_login(self.provider.domain[0])
                self.signal.error.emit(f"Erro geral: {str(e)}")
            except Exception as cleanup_error:
                print(f"Erro no MangaTask: {e}")
                print(f"Erro no cleanup: {cleanup_error}")
                try:
                    self.signal.error.emit(f"Erro crítico: {str(e)}")
                except:
                    pass


class ChaptersTaskSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)


class ChaptersTask(QRunnable):
    def __init__(self, provider, id):
        super().__init__()
        self.provider = provider
        self.id = id
        self.signal = ChaptersTaskSignals()

    def run(self):
        try:
            try:
                chapters = ProviderGetChaptersUseCase(self.provider).execute(self.id)
                self.signal.finished.emit(chapters)
            except Exception as e:
                self.signal.error.emit(f"Erro ao obter capítulos: {str(e)}")
                delete_login(self.provider.domain[0])
                
        except Exception as e:
            try:
                delete_login(self.provider.domain[0])
                self.signal.error.emit(f"Erro geral: {str(e)}")
            except Exception as cleanup_error:
                print(f"Erro no ChaptersTask: {e}")
                print(f"Erro no cleanup: {cleanup_error}")
                try:
                    self.signal.error.emit(f"Erro crítico: {str(e)}")
                except:
                    pass
