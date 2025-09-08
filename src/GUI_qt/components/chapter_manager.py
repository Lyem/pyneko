import re
import os
import json
from typing import List
from PyQt6 import uic
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
from core.providers.domain.entities import Chapter
from GUI_qt.utils.config import get_config
from GUI_qt.utils.load_providers import base_path


class ChapterManager:
    def __init__(self, parent_window, download_callback=None):
        self.parent_window = parent_window
        self.download_callback = download_callback
        self.chapters = []
        self.all_chapters = []
        self.current_dir = os.path.join(base_path(), 'GUI_qt')
        self.assets = os.path.join(self.current_dir, 'assets')
        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    def set_chapters(self, chapters: List[Chapter]):
        self.chapters = chapters
        self.all_chapters = chapters
        self._add_chapters()

    def filter_chapters(self, search_text: str):
        def extract_number(chapter_number):
            match = re.search(r'\d+(\.\d+)?', chapter_number)
            return float(match.group()) if match else None

        text = search_text.strip()
        if not text:
            self.chapters = self.all_chapters
            self._add_chapters()
            return

        try:
            if match := re.match(r'(\d+(\.\d+)?)\*', text):
                number = float(match.group(1))
                self.chapters = [chapter for chapter in self.all_chapters 
                               if (extracted := extract_number(chapter.number)) is not None and extracted >= number]

            elif match := re.match(r'(\d+(\.\d+)?)-(\d+(\.\d+)?)', text):
                start, end = float(match.group(1)), float(match.group(3))
                self.chapters = [chapter for chapter in self.all_chapters 
                               if (extracted := extract_number(chapter.number)) is not None and start <= extracted <= end]

            else:
                self.chapters = [chapter for chapter in self.all_chapters if text in chapter.number]

        except ValueError as e:
            print(f"Error: {e}")
            self.chapters = []

        self._add_chapters()

    def invert_chapters(self):
        self.chapters = self.chapters[::-1]
        self._add_chapters()

    def _add_chapters(self):
        while self.parent_window.verticalChapter.count():
            item = self.parent_window.verticalChapter.takeAt(0)
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
            
            if hasattr(self.parent_window, 'download_status'):
                if any(ch.id == chapter.id for ch, _, _ in self.parent_window.download_status):
                    chapter_ui.download.setEnabled(False)

            if self.download_callback:
                chapter_ui.download.clicked.connect(
                    lambda _, ch=chapter, btn=chapter_ui.download: 
                    self.download_callback(ch, btn)
                )
            chapter_ui.download.setText(download_text)
            self.parent_window.verticalChapter.addWidget(chapter_ui)
        
        self.parent_window.verticalChapter.addItem(self.vertical_spacer)
