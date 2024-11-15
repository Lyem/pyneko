from typing import List
from core.__seedwork.infra.http import Http
from bs4 import BeautifulSoup
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class WordpressEtoshoreMangaTheme(Base):

    def __init__(self) -> None:
        self.get_title = 'h1'
        self.get_chapters_list = 'div.list-box.chapter-list'
        self.chapter = 'li.language-BR > a'
        self.get_chapter_number = 'div.title'
        self.get_div_page = 'div.chapter-image-content'
        self.get_pages = 'noscript > img'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one(self.get_title)
        return Manga(link, title.get_text().strip())

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        chapters_list = soup.select_one(self.get_chapters_list)
        chapter = chapters_list.select(self.chapter)
        title = soup.select_one(self.get_title)
        list = []
        for ch in chapter:
            number = ch.select_one(self.get_chapter_number)
            list.append(Chapter(ch.get('href'), number.get_text().strip(), title.get_text().strip()))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.select_one(self.get_div_page)
        image = images.select(self.get_pages)
        list = []
        for img in image:
            list.append(img.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)

