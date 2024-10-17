from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class YoshukeMangasProvider(Base):
    name = 'Yoshuke Mangas'
    lang = 'pt-Br'
    domain = 'yushukemangas.com'

    def __init__(self) -> None:
        self.base = "https://yushukemangas.com/"
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1')
        return Manga(link, title.get_text().strip())

    def getChapters(self, link: str) -> List[Chapter]:
        list = []
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1')
        while True:
            soup = BeautifulSoup(response.content, 'html.parser')
            chaplist = soup.select_one('section.chapter-list')
            chapters = chaplist.select('a.chapter-link')
            for chapter in chapters:
                number = chapter.select_one('span')
                list.append(Chapter(f"{self.base}{chapter.get('href')}", number.get_text().strip(), title.get_text().strip()))
            next = soup.select_one('a.pagination-next')
            if next:
                response = Http.get(f"{self.base}{next.get("href")}")
            else:
                break

        return list


    def getPages(self, ch: Chapter) -> Pages:
        list = []
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        pages_div = soup.select_one('div.chapter-images')
        images = pages_div.select('img')
        for img in images:
            list.append(f"{self.base}{img.get('src')}")
        return Pages(ch.id, ch.number, ch.name, list)
