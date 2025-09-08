import re
import os
import sys
import subprocess
from PyQt6 import uic
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QApplication, QMessageBox
from tldextract import extract
from clipman import get
from GUI_qt.utils.config import get_config, update_max_download, update_log, update_progress
from GUI_qt.utils.load_providers import import_classes_recursively, base_path
from GUI_qt.workers.manga_worker import MangaTask, ChaptersTask
from GUI_qt.components.chapter_manager import ChapterManager
from GUI_qt.components.progress_manager import ProgressManager
from GUI_qt.components.config_manager import ConfigManager
from GUI_qt.windows.logs import LogWindow
from GUI_qt.windows.websites import WebSiteOpener
from core.config.img_conf import get_config as get_img_config, update_split_height, update_custom_width, update_detection_sensitivity, update_scan_line_step, update_ignorable_pixels
from core.providers.domain.entities import Chapter, Manga


class MangaDownloaderMainWindow:
    def __init__(self, app=None):
        self.provider_selected = None
        self.manga_id_selected = None
        self.providers = import_classes_recursively()

        self.current_dir = os.path.join(base_path(), 'GUI_qt')
        self.assets = os.path.join(self.current_dir, 'assets')

        self.app = app if app is not None else QApplication(sys.argv)
        self.window = uic.loadUi(os.path.join(self.assets, 'main.ui'))

        self.chapter_manager = ChapterManager(
            self.window, self.chapter_download_button_clicked)
        self.progress_manager = ProgressManager(self.window)
        self.config_manager = ConfigManager(self.window)

        self.websites_window = None
        self.log_window = None
        self.init_log = False

        conf = get_config()
        self.pool = QThreadPool.globalInstance()
        self.pool.setMaxThreadCount(conf.max_download)
        self.pool2 = QThreadPool()
        self.pool2.setMaxThreadCount(1)

        self._setup_ui()
        self._connect_signals()
        self._initialize_config()

    def run(self):
        self.window.show()
        return self.app.exec()

    def _setup_ui(self):
        self.window.progress_scroll.hide()
        self.window.simul_qtd.wheelEvent = lambda event: event.ignore()

        conf = get_config()
        if not conf.log and os.environ.get('PYNEKOENV') != 'dev':
            self.window.logs.hide()
        else:
            self.init_log = True
            self.window.dev_check.setChecked(True)
            self.log_window = LogWindow()

        if conf.progress:
            self.window.progress_scroll.show()

        self.window.simul_qtd.setValue(conf.max_download)

    def _connect_signals(self):
        self.window.logs.clicked.connect(self.open_log_window)
        self.window.select_external.clicked.connect(
            self.config_manager.set_external_path_folder)
        self.window.progress.clicked.connect(self.open_progress_window)
        self.window.websites.clicked.connect(self.open_websites)
        self.window.downloadAll.clicked.connect(self.download_all_chapters)
        self.window.link.clicked.connect(self.manga_by_link)
        self.window.invert.clicked.connect(
            self.chapter_manager.invert_chapters)
        self.window.open_folder.clicked.connect(self.open_folder)
        self.window.open_external_folder.clicked.connect(
            self.open_external_folder)
        self.window.config.clicked.connect(self.open_config)
        self.window.config_back.clicked.connect(self.open_home)
        self.window.setSaveFolder.clicked.connect(
            self.config_manager.set_folder)

        self.window.search.textChanged.connect(
            self.chapter_manager.filter_chapters)
        self.window.simul_qtd.textChanged.connect(self.set_max_download)
        self.window.langs.currentTextChanged.connect(
            self.config_manager.lang_changed)
        self.window.langs.wheelEvent = lambda event: event.ignore()
        self.window.format_img.currentTextChanged.connect(
            self.config_manager.img_format_changed)
        self.window.format_img.wheelEvent = lambda event: event.ignore()
        self.window.group_imgs_combo.currentTextChanged.connect(
            self.config_manager.group_imgs_combo_changed)
        self.window.group_imgs_combo.wheelEvent = lambda event: event.ignore()

        self.window.slicer_width_select.currentTextChanged.connect(
            self.config_manager.group_slicer_width_combo_changed)
        self.window.slicer_width_select.wheelEvent = lambda event: event.ignore()
        self.window.slicer_height.textChanged.connect(self.set_slicer_height)
        self.window.slicer_height.wheelEvent = lambda event: event.ignore()
        self.window.slicer_width_spin.textChanged.connect(
            self.set_slicer_width)
        self.window.slicer_width_spin.wheelEvent = lambda event: event.ignore()
        self.window.slicer_detector_select.currentTextChanged.connect(
            self.config_manager.group_detection_type_changed)
        self.window.slicer_detector_select.wheelEvent = lambda event: event.ignore()
        self.window.slicer_detection_sensivity.textChanged.connect(
            self.set_slicer_detection_sensitivity)
        self.window.slicer_detection_sensivity.wheelEvent = lambda event: event.ignore()
        self.window.slicer_scan_line.textChanged.connect(
            self.set_slicer_scan_line)
        self.window.slicer_scan_line.wheelEvent = lambda event: event.ignore()
        self.window.slicer_ignorable_margin.textChanged.connect(
            self.set_slicer_ignorable_horizontal_margin)
        self.window.slicer_ignorable_margin.wheelEvent = lambda event: event.ignore()

        self.window.dev_check.stateChanged.connect(self.toggle_log)
        self.window.group_imgs.toggled.connect(
            self.config_manager.toggle_group_img)
        self.window.external.toggled.connect(
            self.config_manager.external_provider_changed)
        self.window.replacegroupcheckBox.toggled.connect(
            self.config_manager.toggle_group_replace)
        self.window.replaceslicecheckBox.toggled.connect(
            self.config_manager.toggle_slice_replace)
        self.window.slicer_box.toggled.connect(
            self.config_manager.toggle_group_slice)

    def _initialize_config(self):
        self.config_manager.initialize_config()

    def chapter_download_button_clicked(self, chapter: Chapter, download_button):
        try:
            download_button.setEnabled(False)
            self.progress_manager.add_download(chapter, self.provider_selected)
        except Exception as e:
            print(f"Error in chapter download button clicked: {e}")

    def set_chapter(self, chapters):
        self.chapter_manager.set_chapters(chapters)
        self.window.pages.setCurrentIndex(0)

    def set_title(self, manga: Manga):
        self.manga_id_selected = manga.id
        self.window.setWindowTitle(
            f'PyNeko | {manga.name} | {self.provider_selected.name}')
        chapter_task = ChaptersTask(self.provider_selected, manga.id)
        chapter_task.signal.finished.connect(self.set_chapter)
        chapter_task.signal.error.connect(self._manga_by_link_error)
        self.pool2.start(chapter_task)

    def _manga_by_link_error(self, msg: str):
        self.window.pages.setCurrentIndex(0)
        QMessageBox.critical(None, "Erro", str(msg))

    def manga_by_link(self):
        link = get()
        extract_info = extract(link)

        if extract_info.subdomain:
            domain = f"{extract_info.subdomain}.{extract_info.domain}.{extract_info.suffix}"
        else:
            domain = f"{extract_info.domain}.{extract_info.suffix}"

        provider_found = False

        for provider in self.providers:
            for provider_domain in provider.domain:
                def run():
                    nonlocal provider_found
                    self.provider_selected = provider
                    provider_found = True
                    self.window.pages.setCurrentIndex(1)
                    manga_task = MangaTask(provider, link)
                    manga_task.signal.finished.connect(self.set_title)
                    manga_task.signal.error.connect(self._manga_by_link_error)
                    self.pool2.start(manga_task)

                if isinstance(provider_domain, re.Pattern):
                    if provider_domain.match(domain):
                        run()
                        break
                if provider_domain == domain:
                    run()
                    break
            if provider_found:
                break

        if not provider_found:
            self._show_provider_not_found_error(domain)

    def _show_provider_not_found_error(self, domain):
        import json
        config = get_config()
        translations = {}
        with open(os.path.join(self.assets, 'translations.json'), 'r', encoding='utf-8') as file:
            translations = json.load(file)
        translate = translations[config.lang]
        msg = QMessageBox()
        msg.setWindowTitle(translate['error'])
        msg.setText(
            f"{translate['404_provider']} <span style='color:red;'>{domain}</span> {translate['404_provider2']}")
        msg.exec()

    def download_all_chapters(self):
        if self.manga_id_selected is None:
            return

        downloaded_chapter_ids = self.progress_manager.get_downloaded_chapter_ids()

        chapters_to_download = [
            (chapter, self.provider_selected)
            for chapter in self.chapter_manager.chapters
            if chapter.id not in downloaded_chapter_ids
        ]

        if chapters_to_download:
            self.progress_manager.add_multiple_downloads(chapters_to_download)
            self.chapter_manager._add_chapters()

    def set_max_download(self):
        max_qtd = int(self.window.simul_qtd.text())
        update_max_download(max_qtd)
        self.pool.setMaxThreadCount(max_qtd)

    def set_slicer_height(self):
        slicer_height = int(self.window.slicer_height.text())
        update_split_height(slicer_height)

    def set_slicer_width(self):
        slicer_width = int(self.window.slicer_width_spin.text())
        update_custom_width(slicer_width)

    def set_slicer_detection_sensitivity(self):
        sensitivity = int(self.window.slicer_detection_sensivity.text())
        update_detection_sensitivity(sensitivity)

    def set_slicer_scan_line(self):
        scan_line = int(self.window.slicer_scan_line.text())
        update_scan_line_step(scan_line)

    def set_slicer_ignorable_horizontal_margin(self):
        margin = int(self.window.slicer_ignorable_margin.text())
        update_ignorable_pixels(margin)

    def open_folder(self):
        path = get_img_config().save
        if sys.platform.startswith('win'):
            os.startfile(path)
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])

    def open_external_folder(self):
        path = get_config().external_provider_path
        if sys.platform.startswith('win'):
            os.startfile(path)
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])

    def toggle_log(self):
        if not self.init_log:
            if self.window.logs.isHidden():
                self.window.logs.show()
                self.log_window = LogWindow()
                update_log(True)
            else:
                self.window.logs.hide()
                self.log_window = None
                update_log(False)
        else:
            self.init_log = False

    def open_progress_window(self):
        if self.window.progress_scroll.isHidden():
            self.window.progress_scroll.show()
            update_progress(True)
        else:
            self.window.progress_scroll.hide()
            update_progress(False)

    def open_log_window(self):
        if self.log_window:
            self.log_window.show()

    def open_config(self):
        self.window.pages.setCurrentIndex(2)

    def open_home(self):
        self.window.pages.setCurrentIndex(0)

    def open_websites(self):
        if self.websites_window is None:
            self.websites_window = WebSiteOpener(self.providers)
        self.websites_window.show()

    @property
    def download_status(self):
        return self.progress_manager.download_status
