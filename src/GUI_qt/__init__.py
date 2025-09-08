import sys
import os
import json
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from GUI_qt.utils.error_handler import global_exception_handler
from GUI_qt.utils.load_providers import base_path
from GUI_qt.utils.config import get_config
from GUI_qt.windows.loading import LoadingWindow
from GUI_qt.windows.main_window import MangaDownloaderMainWindow
from GUI_qt.workers.update_worker import UpdateThread

sys.excepthook = global_exception_handler

if __name__ == "__main__":
    try:
        try:
            import pyi_splash # type: ignore
            pyi_splash.close()
        except:
            pass

        app = QApplication(sys.argv)

        loading_window = LoadingWindow()
        loading_window.show()

        update_thread = UpdateThread()
        main_app = MangaDownloaderMainWindow(app)
        
        def start_main_app():
            try:
                loading_window.close()
                main_app.window.show()
            except Exception as e:
                print(f"Erro ao iniciar aplicação principal: {e}")
                global_exception_handler(type(e), e, e.__traceback__)

        update_thread.finished.connect(start_main_app)
        update_thread.start()

        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Erro crítico na inicialização: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        try:
            config = get_config()
            translations = {}
            assets_path = os.path.join(os.path.join(base_path(), 'GUI_qt'), 'assets')
            
            with open(os.path.join(assets_path, 'translations.json'), 'r', encoding='utf-8') as file:
                translations = json.load(file)
            
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            language = config.lang if config else 'en'
            if language not in translations:
                language = 'en'
                
            translate = translations[language]
            
            error_title = translate.get('error', 'Erro')
            app_error_msg = translate.get('app_error', 'Erro na aplicação:')
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(error_title)
            msg_box.setText(f"{app_error_msg} {str(e)}")
            msg_box.setDetailedText(traceback.format_exc())
            msg_box.exec()
            
        except Exception as fallback_error:
            print(f"Erro crítico no fallback: {fallback_error}")
            print(f"Erro original: {e}")
            
            try:
                app = QApplication.instance()
                if app is None:
                    app = QApplication(sys.argv)
                    
                QMessageBox.critical(None, "Erro Crítico", 
                                   f"Erro fatal na aplicação:\n{str(e)}\n\nVerifique os logs para mais detalhes.")
            except:
                print("ERRO FATAL: Não foi possível exibir interface de erro")
                print(f"Erro: {e}")
                sys.exit(1)
