from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QWidget, QSpacerItem, QSizePolicy, QMessageBox
from PyQt6.QtCore import QThreadPool
from GUI_qt.workers.download_worker import DownloadWorker


class ProgressManager:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.download_status = []

    def add_download(self, chapter, provider):
        runnable = DownloadWorker(chapter, provider)
        self.download_status.append((chapter, provider, runnable))
        self._update_progress_ui()

    def add_multiple_downloads(self, chapters_and_providers):
        for chapter, provider in chapters_and_providers:
            runnable = DownloadWorker(chapter, provider)
            self.download_status.append((chapter, provider, runnable))
        self._update_progress_ui()

    def _update_progress_ui(self):
        for download in self.download_status:
            ch, provider, runnable = download

            groupbox = self.parent_window.findChild(QGroupBox, f'groupboxprovider{provider.name}')
            layout = self.parent_window.findChild(QVBoxLayout, f"layoutprovider{provider.name}")
            if groupbox is None:
                groupbox = QGroupBox()
                groupbox.setTitle(provider.name)
                groupbox.setObjectName(f'groupboxprovider{provider.name}')
                layout = QVBoxLayout()
                layout.setObjectName(f"layoutprovider{provider.name}")
                groupbox.setLayout(layout)
                self.parent_window.verticalProgress.addWidget(groupbox)

            groupbox2 = self.parent_window.findChild(QGroupBox, f'groupboxmedia{ch.name}')
            layout2 = self.parent_window.findChild(QVBoxLayout, f"layoutmedia{ch.name}")
            if groupbox2 is None:
                groupbox2 = QGroupBox()
                groupbox2.setTitle(ch.name)
                groupbox2.setObjectName(f'groupboxmedia{ch.name}')
                layout2 = QVBoxLayout()
                layout2.setObjectName(f"layoutmedia{ch.name}")
                groupbox2.setLayout(layout2)
                layout.addWidget(groupbox2)

            layout_item = self.parent_window.findChild(QHBoxLayout, f'chaptermedia{ch.name}{ch.id}{provider.name}')
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
                
                QThreadPool.globalInstance().start(runnable)

                progress_layout.addWidget(progress_bar)
                layout_item.addLayout(progress_layout)
                layout2.addWidget(widget)

        for child in self.parent_window.findChildren(QWidget):
            layout = child.layout()
            if layout and layout.objectName().startswith('layoutmedia'):
                for i in reversed(range(layout.count())):
                    item = layout.itemAt(i)
                    if isinstance(item, QSpacerItem):
                        layout.removeItem(item)
                layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def clear_download_status(self):
        self.download_status.clear()

    def get_downloaded_chapter_ids(self):
        return {ch.id for ch, *_ in self.download_status}
