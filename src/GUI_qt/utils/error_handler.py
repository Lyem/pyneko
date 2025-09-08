import sys
import os
import json
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from GUI_qt.utils.config import get_config
from GUI_qt.utils.load_providers import base_path


class SafeSlotWrapper:
    @staticmethod
    def protect(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Erro capturado no slot {func.__name__}: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                
                try:
                    app = QApplication.instance()
                    if app:
                        QMessageBox.critical(None, "Erro", f"Erro em {func.__name__}: {str(e)}")
                except:
                    pass
                    
        return wrapper


def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    print(f"[ERRO GLOBAL CAPTURADO] {error_msg}", file=sys.stderr)
    
    try:
        config = get_config()
        translations = {}
        assets_path = os.path.join(os.path.join(base_path(), 'GUI_qt'), 'assets')
        
        with open(os.path.join(assets_path, 'translations.json'), 'r', encoding='utf-8') as file:
            translations = json.load(file)
        
        language = config.lang if config else 'en'
        if language not in translations:
            language = 'en'
        
        translate = translations[language]
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        error_title = translate.get('error', 'Erro')
        app_error_msg = translate.get('app_error', 'Erro na aplicação:')
        
        simple_error = str(exc_value) if exc_value else "Erro desconhecido"
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(error_title)
        msg_box.setText(f"{app_error_msg} {simple_error}")
        msg_box.setDetailedText(error_msg)
        msg_box.exec()
        
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao exibir erro: {e}", file=sys.stderr)
        print(f"[ERRO ORIGINAL] {error_msg}", file=sys.stderr)
