import re
import os
import sys
import json
import subprocess
from PyQt6 import uic
from typing import List
from clipman import init, get
from tldextract import extract
from GUI_qt.logs import LogWindow
from GUI_qt.version import version
from GUI_qt.loading import LoadingWindow
from GUI_qt.websites import WebSiteOpener
from GUI_qt.new_version import NewVersion
from core.config.login_data import delete_login
from core.providers.domain.entities import Chapter, Manga
from GUI_qt.git import update_providers, get_last_version
from core.slicer.application.use_cases import SlicerUseCase
from core.group_imgs.application.use_cases import GroupImgsUseCase
from GUI_qt.load_providers import import_classes_recursively, base_path
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject, QLocale, QThread
from GUI_qt.config import get_config, update_lang, update_progress, update_max_download, update_log, update_external_path, update_external
from core.providers.application.use_cases import ProviderMangaUseCase, ProviderGetChaptersUseCase, ProviderGetPagesUseCase, ProviderDownloadUseCase, ProviderLoginUseCase
from PyQt6.QtWidgets import QApplication, QMessageBox, QSpacerItem, QSizePolicy, QApplication, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFileDialog, QWidget
from core.config.img_conf import (
    get_config as get_img_config,
    update_img, update_save,
    update_automatic_width,
    update_custom_width,
    update_detection_sensitivity,
    update_detection_type,
    update_group,
    update_group_format,
    update_ignorable_pixels,
    update_scan_line_step,
    update_slice,
    update_split_height,
    update_slice_replace_original_files,
    update_group_replace_original_files
)

class WorkerSignals(QObject):
    progress_changed = pyqtSignal(int)
    download_error = pyqtSignal(str)
    color = pyqtSignal(str)
    name = pyqtSignal(str)

class DownloadRunnable(QRunnable):
    def __init__(self, ch, provider):
        super().__init__()
        self.ch = ch
        self.provider = provider
        self.signals = WorkerSignals()
        self.current_dir = os.path.join(base_path(), 'GUI_qt')
        self.assets = os.path.join(self.current_dir, 'assets')

    def run(self):
        try:
            img_conf = get_img_config()
            conf = get_config()
            pages = ProviderGetPagesUseCase(self.provider).execute(self.ch)
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
                self.signals.progress_changed.emit(int(value))

            ch = ProviderDownloadUseCase(self.provider).execute(pages=pages, fn=update_progress_bar)

            if img_conf.slice:
                self.signals.name.emit(translation['slicing'])
                self.signals.progress_changed.emit(0)
                set_progress_bar_style("#0080FF")
                ch = SlicerUseCase().execute(ch, update_progress_bar)

            if img_conf.group:
                self.signals.name.emit(translation['grouping'])
                self.signals.progress_changed.emit(0)
                set_progress_bar_style("#FFA500")
                GroupImgsUseCase().execute(ch, update_progress_bar)
                self.signals.progress_changed.emit(100)

        except Exception as e:
            set_progress_bar_style("red")
            self.signals.download_error.emit(f'{self.ch.name} \n {self.ch.number} \n {str(e)}')
            delete_login(self.provider.domain[0])

class UpdateThread(QThread):
    finished = pyqtSignal()

    def run(self):
        init()
        if os.environ.get('PYNEKOENV') != 'dev':
            update_providers()
            if version != get_last_version():
                NewVersion()
        self.finished.emit()

class MangaTaskSignals(QObject):
    finished = pyqtSignal(Manga)
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
                ProviderLoginUseCase(self.provider).execute()
            manga = ProviderMangaUseCase(self.provider).execute(self.link)
            self.signal.finished.emit(manga)
        except Exception as e:
            delete_login(self.provider.domain[0])
            self.signal.error.emit(str(e))


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
            chapters = ProviderGetChaptersUseCase(self.provider).execute(self.id)
            self.signal.finished.emit(chapters)
        except Exception as e:
            self.signal.error.emit(str(e))
            delete_login(self.provider.domain[0])

class MangaDownloaderApp:
    def __init__(self):
        self.provider_selected = None
        self.manga_id_selectd = None
        self.chapters = []
        self.all_chapters = []
        self.download_status = []

        self.providers = import_classes_recursively()
        self.current_dir = os.path.join(base_path(), 'GUI_qt')
        self.assets = os.path.join(self.current_dir, 'assets')

        self.app = QApplication(sys.argv)
        self.window = uic.loadUi(os.path.join(self.assets, 'main.ui'))
        self.window.show()

        self.window.progress_scroll.hide()
        self.window.logs.clicked.connect(self.open_log_window)

        self.window.select_external.clicked.connect(self.set_external_path_folder)
        self.window.progress.clicked.connect(self.open_progress_window)
        self.window.websites.clicked.connect(self.open_websites)
        self.window.downloadAll.clicked.connect(self.download_all_chapters)
        self.window.link.clicked.connect(self.manga_by_link)
        self.window.invert.clicked.connect(self.invert_chapters)
        self.window.search.textChanged.connect(self.filter_chapters)
        self.window.simul_qtd.textChanged.connect(self.setMaxDownload)
        self.window.simul_qtd.wheelEvent = lambda event: event.ignore()
        self.window.dev_check.stateChanged.connect(self.toogle_log)
        self.window.group_imgs.toggled.connect(self.toogle_group_img)
        self.window.external.toggled.connect(self.externalProviderChanged)
        self.window.replacegroupcheckBox.toggled.connect(self.toogle_group_replace)
        self.window.replaceslicecheckBox.toggled.connect(self.toogle_slice_replace)
        self.window.slicer_box.toggled.connect(self.toogle_group_slice)
        self.window.config.clicked.connect(self.open_config)
        self.window.open_folder.clicked.connect(self.open_folder)
        self.window.open_external_folder.clicked.connect(self.open_external_folder)
        self.window.config_back.clicked.connect(self.open_home)
        self.window.langs.currentTextChanged.connect(self.langChanged)
        self.window.langs.wheelEvent = lambda event: event.ignore()
        self.window.format_img.currentTextChanged.connect(self.imgFormatChanged)
        self.window.format_img.wheelEvent = lambda event: event.ignore()
        self.window.group_imgs_combo.currentTextChanged.connect(self.groupImgsComboChanged)
        self.window.slicer_width_select.currentTextChanged.connect(self.groupSlicerWidthComboChanged)
        self.window.slicer_width_select.wheelEvent = lambda event: event.ignore()
        self.window.slicer_height.textChanged.connect(self.setSlicerHeight)
        self.window.slicer_width_spin.textChanged.connect(self.setSlicerWidth)
        self.window.slicer_detector_select.currentTextChanged.connect(self.groupDetectionTypeChanged)
        self.window.slicer_detector_select.wheelEvent = lambda event: event.ignore()
        self.window.slicer_detection_sensivity.textChanged.connect(self.setSlicerDetectionSensivity)
        self.window.slicer_scan_line.textChanged.connect(self.setSlicerScanLine)
        self.window.slicer_ignorable_margin.textChanged.connect(self.setSlicerIgnorableHorizontalMargin)
        self.window.setSaveFolder.clicked.connect(self.setFolder)


        self.websites_window = None

        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.initial_data = True
        self.langChanged()
        self.imgFormatChanged()
        conf = get_config()
        self.setFolder()
        self.set_external_path_folder()

        if conf.progress:
            self.window.progress_scroll.show()

        self.init_log = False

        if not conf.log and os.environ.get('PYNEKOENV') != 'dev':
            self.window.logs.hide()
        else:
            self.init_log = True
            self.window.dev_check.setChecked(True)
            self.log_window = LogWindow()

        data = get_img_config()
        self.window.group_imgs.setChecked(data.group)
        self.window.slicer_box.setChecked(data.slice)
        if conf.external_provider:
            self.window.external.setChecked(conf.external_provider)
        self.window.replaceslicecheckBox.setChecked(data.slice_replace_original_files)
        self.window.replacegroupcheckBox.setChecked(data.group_replace_original_files)
        self.window.group_imgs_combo.setCurrentText(data.group_format)
        self.window.group_imgs_combo.wheelEvent = lambda event: event.ignore()
        self.window.slicer_height.setValue(data.split_height)
        self.window.slicer_height.wheelEvent = lambda event: event.ignore()
        self.window.slicer_width_spin.setValue(data.custom_width)
        self.window.slicer_width_spin.wheelEvent = lambda event: event.ignore()
        self.window.slicer_detection_sensivity.setValue(data.detection_sensitivity)
        self.window.slicer_detection_sensivity.wheelEvent = lambda event: event.ignore()
        self.window.slicer_scan_line.setValue(data.scan_line_step)
        self.window.slicer_scan_line.wheelEvent = lambda event: event.ignore()
        self.window.slicer_ignorable_margin.setValue(data.ignorable_pixels)
        self.window.slicer_ignorable_margin.wheelEvent = lambda event: event.ignore()
        if(data.automatic_width):
            self.window.slicer_width_select.setCurrentIndex(1)
        else:
            if(data.custom_width == 0):
                self.window.slicer_width_select.setCurrentIndex(0)
            else:
                self.window.slicer_width_select.setCurrentIndex(2)
        width_select_index = self.window.slicer_width_select.currentIndex()
        if(width_select_index < 2):
            self.window.slicer_width_spin_label.hide()
            self.window.slicer_width_spin.hide()
        if(data.detection_type == 'pixel'):
            self.window.slicer_detector_select.setCurrentIndex(0)
        else:
            self.window.slicer_detector_select.setCurrentIndex(1)
            self.window.slicer_detection_sensivity_label.hide()
            self.window.slicer_detection_sensivity.hide()
            self.window.slicer_scan_line_label.hide()
            self.window.slicer_scan_line.hide()
            self.window.slicer_ignorable_margin_label.hide()
            self.window.slicer_ignorable_margin.hide()
        self.initial_data = False

        self.pool = QThreadPool.globalInstance()
        self.pool.setMaxThreadCount(conf.max_download)
        self.window.simul_qtd.setValue(conf.max_download)
        self.pool2 = QThreadPool()
        self.pool2.setMaxThreadCount(1)


    def run(self):
        sys.exit(self.app.exec())


    def setFolder(self):
        data = get_img_config()
        if not self.initial_data:
            folder_path = QFileDialog.getExistingDirectory(self.window, "Select Folder", data.save)
            if folder_path:
                update_save(folder_path)
                self.window.path.setText(folder_path)
        else:
            self.window.path.setText(data.save)
    
    def set_external_path_folder(self):
        data = get_config()
        if not self.initial_data:
            folder_path = QFileDialog.getExistingDirectory(self.window, "Select Folder", data.external_provider_path)
            if folder_path:
                update_external_path(folder_path)
                self.window.selected_external.setText(folder_path)
        else:
            if data.external_provider_path:
                self.window.selected_external.setText(data.external_provider_path)
    
    def externalProviderChanged(self, checked):
        if not self.initial_data:
            data = get_config()
            if not data.external_provider_path:
                folder_path = QFileDialog.getExistingDirectory(self.window, "Select Folder", data.external_provider_path)
                if folder_path:
                    update_external_path(folder_path)
                    self.window.selected_external.setText(folder_path)
                    update_external(checked)
            else:
                update_external(checked)

    def chapter_download_button_clicked(self, ch: Chapter, download_button):
        try:
            download_button.setEnabled(False)

            runnable = DownloadRunnable(ch, self.provider_selected)
            self.download_status.append((ch, self.provider_selected, runnable))
            self._load_progress()
        except Exception as e:
            print(f"Error in chapter download button clicked: {e}")

    def _add_chapters(self):
        while self.window.verticalChapter.count():
            item = self.window.verticalChapter.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        config = get_config()
        with open(os.path.join(self.assets, 'translations.json'), 'r', encoding='utf-8') as file:
            translations = json.load(file)
        download_text = translations[config.lang]['download']
        for chapter in self.chapters:
            chapter_ui = uic.loadUi(os.path.join(self.assets, 'chapter.ui'))
            chapter_ui.numberLabel.setText(str(chapter.number))
            if any(ch.id == chapter.id for ch, _, _ in self.download_status):
                chapter_ui.download.setEnabled(False)

            chapter_ui.download.clicked.connect(
                lambda _, ch=chapter, btn=chapter_ui.download: self.chapter_download_button_clicked(ch, btn)
            )
            chapter_ui.download.setText(download_text)
            self.window.verticalChapter.addWidget(chapter_ui)
        self.window.verticalChapter.addItem(self.vertical_spacer)

    def filter_chapters(self):
        def extract_number(chapter_number):
            match = re.search(r'\d+(\.\d+)?', chapter_number)
            return float(match.group()) if match else None

        text = self.window.search.text().strip()
        if not text:
            self.chapters = self.all_chapters
            self._add_chapters()
            return

        try:
            if match := re.match(r'(\d+(\.\d+)?)\*', text):
                number = float(match.group(1))
                self.chapters = [chapter for chapter in self.all_chapters if (extracted := extract_number(chapter.number)) is not None and extracted >= number]

            elif match := re.match(r'(\d+(\.\d+)?)-(\d+(\.\d+)?)', text):
                start, end = float(match.group(1)), float(match.group(3))
                self.chapters = [chapter for chapter in self.all_chapters if (extracted := extract_number(chapter.number)) is not None and start <= extracted <= end]

            else:
                self.chapters = [chapter for chapter in self.all_chapters if text in chapter.number]

        except ValueError as e:
            print(f"Error: {e}")
            self.chapters = []

        self._add_chapters()

    def invert_chapters(self):
        self.chapters = self.chapters[::-1]
        self._add_chapters()

    def set_chapter(self, chapters: List[Chapter]):
        self.chapters = chapters
        self.all_chapters = chapters
        self._add_chapters()
        self.window.pages.setCurrentIndex(0)

    def set_title(self, manga: Manga):
        self.manga_id_selectd = manga.id
        self.window.setWindowTitle(f'PyNeko | {manga.name} | {self.provider_selected.name}')
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
        provider_find = False
        for provider in self.providers:
            for provider_domain in provider.domain:
                def run():
                    nonlocal provider_find
                    self.provider_selected = provider
                    provider_find = True
                    self.window.pages.setCurrentIndex(1)
                    manga_task = MangaTask(provider, link)
                    manga_task.signal.finished.connect(self.set_title)
                    manga_task.signal.error.connect(self._manga_by_link_error)
                    self.pool2.start(manga_task)
                if isinstance(provider_domain, re.Pattern):
                    if provider_domain.match(domain):
                        run()
                if provider_domain == domain:
                    run()
        if provider_find == False:
            config = get_config()
            translations = {}
            with open(os.path.join(self.assets, 'translations.json'), 'r', encoding='utf-8') as file:
                translations = json.load(file)
            translate = translations[config.lang]
            msg = QMessageBox()
            msg.setWindowTitle(translate['error'])
            msg.setText(f"{translate['404_provider']} <span style='color:red;'>{domain}</span> {translate['404_provider2']}")
            msg.exec()

    def download_all_chapters(self):
        if self.manga_id_selectd is None:
            return

        downloaded_chapter_ids = {ch.id for ch, *_ in self.download_status}

        chapters_to_download = filter(
            lambda chapter: chapter.id not in downloaded_chapter_ids, self.chapters
        )

        self.download_status.extend(
            (chapter, self.provider_selected, DownloadRunnable(chapter, self.provider_selected))
            for chapter in chapters_to_download
        )

        self._load_progress()
        self._add_chapters()

    def _load_progress(self):
        for download in self.download_status:
            ch, provider, runnable = download

            groupbox = self.window.findChild(QGroupBox, f'groupboxprovider{provider.name}')
            layout = self.window.findChild(QVBoxLayout, f"layoutprovider{provider.name}")
            if groupbox is None:
                groupbox = QGroupBox()
                groupbox.setTitle(provider.name)
                groupbox.setObjectName(f'groupboxprovider{provider.name}')
                layout = QVBoxLayout()
                layout.setObjectName(f"layoutprovider{provider.name}")
                groupbox.setLayout(layout)
                self.window.verticalProgress.addWidget(groupbox)

            groupbox2 = self.window.findChild(QGroupBox, f'groupboxmedia{ch.name}')
            layout2 = self.window.findChild(QVBoxLayout, f"layoutmedia{ch.name}")
            if groupbox2 is None:
                groupbox2 = QGroupBox()
                groupbox2.setTitle(ch.name)
                groupbox2.setObjectName(f'groupboxmedia{ch.name}')
                layout2 = QVBoxLayout()
                layout2.setObjectName(f"layoutmedia{ch.name}")
                groupbox2.setLayout(layout2)
                layout.addWidget(groupbox2)

            layout_item = self.window.findChild(QHBoxLayout, f'chaptermedia{ch.name}{ch.id}{provider.name}')
            if layout_item is None:
                layout_item = QHBoxLayout()
                layout_item.setObjectName(f'chaptermedia{ch.name}{ch.id}{provider.name}')
                widget = QWidget()
                widget.setLayout(layout_item)

                label_layout = QVBoxLayout()
                empty_label = QLabel(" ")
                label_layout.addWidget(empty_label)
                label = QLabel()
                label.setText(str(ch.number))
                label_layout.addWidget(label)
                layout_item.addLayout(label_layout)

                progress_layout = QVBoxLayout()
                download_label = QLabel(" ")
                progress_layout.addWidget(download_label)
                progress_bar = QProgressBar()

                runnable.signals.progress_changed.connect(lambda value, pb=progress_bar: pb.setValue(value))
                runnable.signals.color.connect(lambda value, pb=progress_bar: pb.setStyleSheet(value))
                runnable.signals.name.connect(lambda value, lbl=download_label: lbl.setText(value))
                runnable.signals.download_error.connect(lambda value, error=QMessageBox: error.critical(None, "Error", f"{str(value)}"))
                self.pool.start(runnable)

                progress_layout.addWidget(progress_bar)
                layout_item.addLayout(progress_layout)
                layout2.addWidget(widget)

        for child in self.window.findChildren(QWidget):
            layout = child.layout()
            if layout and layout.objectName().startswith('layoutmedia'):
                for i in reversed(range(layout.count())):
                    item = layout.itemAt(i)
                    if isinstance(item, QSpacerItem):
                        layout.removeItem(item)
                layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def imgFormatChanged(self, img=None):
        if not img:
            data = get_img_config()
            self.window.format_img.setCurrentText(data.img)
        else:
            update_img(img)

    def groupImgsComboChanged(self, img=None):
        if img:
            update_group_format(img)

    def groupDetectionTypeChanged(self, model=None):
        if not self.initial_data:
            if model:
                detection_type_index = self.window.slicer_detector_select.currentIndex()
                if(detection_type_index == 0):
                    update_detection_type('pixel')
                    self.window.slicer_detection_sensivity_label.show()
                    self.window.slicer_detection_sensivity.show()
                    self.window.slicer_scan_line_label.show()
                    self.window.slicer_scan_line.show()
                    self.window.slicer_ignorable_margin_label.show()
                    self.window.slicer_ignorable_margin.show()
                else:
                    update_detection_type(None)
                    self.window.slicer_detection_sensivity_label.hide()
                    self.window.slicer_detection_sensivity.hide()
                    self.window.slicer_scan_line_label.hide()
                    self.window.slicer_scan_line.hide()
                    self.window.slicer_ignorable_margin_label.hide()
                    self.window.slicer_ignorable_margin.hide()

    def groupSlicerWidthComboChanged(self, model=None):
        if not self.initial_data:
            if model:
                width_select_index = self.window.slicer_width_select.currentIndex()
                if(width_select_index < 2):
                    update_custom_width(0)
                    if(width_select_index == 1):
                        update_automatic_width(True)
                    else:
                        update_automatic_width(False)
                    self.window.slicer_width_spin_label.hide()
                    self.window.slicer_width_spin.hide()
                else:
                    update_automatic_width(False)
                    self.window.slicer_width_spin_label.show()
                    self.window.slicer_width_spin.show()

    def setMaxDownload(self):
        max_qtd = int(self.window.simul_qtd.text())
        update_max_download(max_qtd)
        self.pool.setMaxThreadCount(max_qtd)

    def setSlicerHeight(self):
        slicer_height = int(self.window.slicer_height.text())
        update_split_height(slicer_height)

    def setSlicerWidth(self):
        slicer_width = int(self.window.slicer_width_spin.text())
        update_custom_width(slicer_width)

    def setSlicerDetectionSensivity(self):
        sensivity = int(self.window.slicer_detection_sensivity.text())
        update_detection_sensitivity(sensivity)

    def setSlicerScanLine(self):
        scan_line = int(self.window.slicer_scan_line.text())
        update_scan_line_step(scan_line)

    def setSlicerIgnorableHorizontalMargin(self):
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

    def langChanged(self, lang=None):
        translations = {}
        with open(os.path.join(self.assets, 'translations.json'), 'r', encoding='utf-8') as file:
            translations = json.load(file)

        language = lang
        if not lang:
            config = get_config()
            if not config:
                language = QLocale.system().name()
                update_lang(language)
            else:
                language = config.lang
            if language not in translations:
                language = 'en'
            self.window.langs.setCurrentText(language)
        else:
            update_lang(language)

        translation = translations[language]

        self.window.websites.setText(translation['websites'])
        self.window.link.setText(translation['paste'])
        self.window.downloadAll.setText(translation['download_all'])
        self.window.invert.setText(translation['invert'])
        self.window.search.setPlaceholderText(translation['search_caps'])
        self.window.progress.setText(translation['progress'])
        self.window.label.setText(translation['loading'])
        self.window.config.setText(translation['config'])
        self.window.config_back.setText(translation['back'])
        self.window.language_label.setText(translation['language'])
        self.window.img_format.setText(translation['format'])
        self.window.open_folder.setText(translation['open_folder'])
        self.window.open_external_folder.setText(translation['open_folder'])
        self.window.path_label.setText(translation['path_label'])
        self.window.simul_label.setText(translation['download_qtd'])
        self.window.dev_label.setText(translation['dev_label'])
        self.window.dev_check.setText(translation['dev_check'])
        self.window.group_imgs.setTitle(translation['group_images'])
        self.window.slicer_box.setTitle(translation['slicer'])
        self.window.slicer_height_label.setText(translation['height_output'])
        self.window.slicer_width_label.setText(translation['width_enforcement_type'])
        self.window.slicer_width_spin_label.setText(translation['width_custom'])
        self.window.slicer_detector_label.setText(translation['detector_type'])
        self.window.slicer_width_select.clear()
        self.window.slicer_width_select.addItems([
            translation['no_enforcement'],
            translation['automatic_uniform_width'],
            translation['user_customized_width']
        ])
        self.window.slicer_detector_select.clear()
        self.window.slicer_detector_select.addItems([
            translation['smart_pixel'],
            translation['direct_slicing'],
        ])
        self.window.slicer_detection_sensivity_label.setText(translation['detection_sensitivity'])
        self.window.slicer_scan_line_label.setText(translation['scan_line_step'])
        self.window.slicer_ignorable_margin_label.setText(translation['ignore_horizontal_margins'])
        self.window.replaceslicecheckBox.setText(translation['overwrite'])
        self.window.replacegroupcheckBox.setText(translation['overwrite'])
        self.window.external.setTitle(translation['external'])

    def toogle_group_img(self, checked):
        if not self.initial_data:
            update_group(checked)

    def toogle_group_slice(self, checked):
        if not self.initial_data:
            update_slice(checked)

    def toogle_group_replace(self, checked):
        if not self.initial_data:
            update_group_replace_original_files(checked)

    def toogle_slice_replace(self, checked):
        if not self.initial_data:
            update_slice_replace_original_files(checked)

    def toogle_log(self):
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
        self.log_window.show()

    def open_config(self):
        self.window.pages.setCurrentIndex(2)

    def open_home(self):
        self.window.pages.setCurrentIndex(0)

    def open_websites(self):
        if self.websites_window is None:
            self.websites_window = WebSiteOpener(self.providers)

        self.websites_window.show()

if __name__ == "__main__":
    try:

        if os.environ.get('PYNEKOENV') == 'dev':
            from jurigged import watch
            watch(str(base_path()))

        try:
            import pyi_splash # type: ignore
            pyi_splash.close()
        except:
            pass

        update = QApplication(sys.argv)

        loading_window = LoadingWindow()
        loading_window.show()

        update_thread = UpdateThread()
        update_thread.finished.connect(loading_window.close)

        update_thread.start()

        update.exec()

        MangaDownloaderApp().run()
    except Exception as e:
        config = get_config()
        translations = {}
        with open(os.path.join(os.path.join(os.path.join(base_path(), 'GUI_qt'), 'assets'), 'translations.json'), 'r', encoding='utf-8') as file:
            translations = json.load(file)
        new = QApplication(sys.argv)
        translate = translations[config.lang]
        QMessageBox.critical(None, translate['error'], f"{translate['app_error']} {str(e)}")
