import os
import sys
import threading
from PyQt6 import uic
from time import sleep
from clipman import init, get
from tldextract import extract
from PyQt6.QtWidgets import QApplication, QMessageBox
from concurrent.futures import ThreadPoolExecutor
from GUI_qt.load_providers import import_classes_recursively, base_path
from core.providers.domain.chapter_entity import Chapter
from core.providers.application.use_cases import ProviderMangaUseCase, ProviderGetChaptersUseCase, ProviderGetPagesUseCase, ProviderDownloadUseCase

class MangaDownloaderApp:
    def __init__(self):
        self.providers = import_classes_recursively()
        self.provider_selected = None
        self.mangas = []
        self.manga_id_selectd = None

        self.running = True
        self.queue_download = []
        self.downloading = []
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.clock_worker = 1
        self.max_concurrent_downloads = 3

        self.current_dir = os.path.join(base_path(), 'GUI_qt')
        self.assets = os.path.join(self.current_dir, 'assets')

        self.app = QApplication(sys.argv)
        self.window = uic.loadUi(os.path.join(self.assets, 'main.ui'))
        self.window.closeEvent = self.closeEvent
        self.window.CopyLinkButton.clicked.connect(self.manga_by_link)
        self.window.downloadAll.clicked.connect(self.download_all_chapters)
        self.window.downloadAll.setEnabled(False)
        self.window.providersButton.setEnabled(False)
        self.window.LoadButton.setEnabled(False)
        self.window.mangaFilter.setEnabled(False)
        self.window.chapterFilter.setEnabled(False)
        self.window.show()

        self.executor.submit(self.worker)

    def worker(self):
        while self.running:
            if len(self.queue_download) > 0:
                if len(self.downloading) < self.max_concurrent_downloads:
                    self.downloading.append('item')
                    pages, update_progress_bar = self.queue_download[0]
                    del self.queue_download[0]
                    threading.Thread(target=self.make_download, args=(pages, update_progress_bar)).start()
            sleep(self.clock_worker)
    
    def make_download(self, pages, update_progress_bar):
        try:
            ProviderDownloadUseCase(self.provider_selected).execute(pages=pages, fn=update_progress_bar)
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Falha no download {str(e)}")
        self.downloading.pop()

    def chapter_download_button_clicked(self, ch: Chapter, progress_bar, download_button):
        download_button.setEnabled(False)
        progress_bar.setVisible(True)
        pages = ProviderGetPagesUseCase(self.provider_selected).execute(ch)
        def update_progress_bar(value):
            progress_bar.setValue(int(value))
        # ProviderDownloadUseCase(self.provider_selected).execute(pages=pages, fn=update_progress_bar)
        self.queue_download.append((pages, update_progress_bar))

    def get_chapters(self, item):
        index = self.window.mangaList.row(item)
        self.manga_id_selectd = str(self.mangas[index].id)
        chapters = ProviderGetChaptersUseCase(self.provider_selected).execute(self.manga_id_selectd)
        for i in reversed(range(self.window.verticalChapter.count())):
            widget = self.window.verticalChapter.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        for chapter in chapters:
            chapter_ui = uic.loadUi(os.path.join(self.assets, 'chapter.ui'))
            chapter_ui.numberLabel.setText(str(chapter.number))
            chapter_ui.ChapterprogressBar.setVisible(False)
            chapter_ui.read.setEnabled(False)
            chapter_ui.download.clicked.connect(lambda _, ch=chapter, progress_bar=chapter_ui.ChapterprogressBar, download_button=chapter_ui.download: self.chapter_download_button_clicked(ch, progress_bar, download_button))
            self.window.verticalChapter.addWidget(chapter_ui)

    def download_all_chapters(self):
        pass
        # if self.manga_id_selectd != None:
        #     chapters = ProviderGetChaptersUseCase(self.provider_selected).execute(self.manga_id_selectd)
        #     for i in range(self.window.verticalChapter.count()):
        #         chapter_ui = self.window.verticalChapter.itemAt(i).widget()
        #         for ch in chapters:
        #             if str(ch.number) == chapter_ui.numberLabel.text():
        #                 progress_bar = chapter_ui.ChapterprogressBar
        #                 progress_bar.setVisible(True)
        #     for i in range(self.window.verticalChapter.count()):
        #         chapter_ui = self.window.verticalChapter.itemAt(i).widget()
        #         for ch in chapters:
        #             if str(ch.number) == chapter_ui.numberLabel.text():
        #                 progress_bar = chapter_ui.ChapterprogressBar
        #                 pages = ProviderGetPagesUseCase(self.provider_selected).execute(ch.id)
        #                 def update_progress_bar(value):
        #                     progress_bar.setValue(int(value))
        #                 self.queue_download.append((pages, update_progress_bar))
        #                 sleep(self.clock_worker)

    def manga_by_link(self):
        if self.window.mangaList.count() > 0:
            self.window.mangaList.clear() 
        link = get()
        extract_info = extract(link)
        domain = f"{extract_info.domain}.{extract_info.suffix}"
        for provider in self.providers:
            if provider.domain == domain:
                self.provider_selected = provider
                manga = ProviderMangaUseCase(provider).execute(link)
                self.mangas = []
                self.mangas.append(manga)
                self.window.mangaList.addItem(manga.name)
                self.window.mangaList.itemClicked.connect(self.get_chapters)
                QApplication.processEvents()

    def run(self):
        sys.exit(self.app.exec())
    
    def closeEvent(self, event):
        self.running = False
        event.accept()

if __name__ == "__main__":
    try:
        init()
        app = MangaDownloaderApp()
        app.run()
    except Exception as e:
        new = QApplication(sys.argv)
        QMessageBox.critical(None, "Erro", f"A aplicação encontrou o seguinte erro e precisa ser fechada: {str(e)}")

