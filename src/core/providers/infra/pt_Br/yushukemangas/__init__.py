from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class YushukeMangasProvider(Base):
    name = 'Yushuke Mangas'
    lang = 'pt_Br'
    domain = ['new.yushukemangas.com']

    def __init__(self) -> None:
        self.base = 'https://new.yushukemangas.com'
        self.last_logo = '/uploads/começo_e_fim/fim.png'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div.manga-title-row h1')

        return Manga(link, title.get_text(strip=True))

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div.manga-title-row h1')
        get_chapter = soup.select('div#chapters-container a')
        list = []
        for ch in get_chapter:
            number = ch.select_one('span.chapter-number')
            list.append(Chapter(f'{self.base}{ch.get('href')}', number.get_text(strip=True), title.get_text(strip=True)))
        return list
    
    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        get_pages = soup.select('div.manga-container img')
        list = []
        for pgs in get_pages:
            pages = pgs.get('src')
            if pages == self.last_logo:
                continue
            list.append(f'{self.base}{pages}')
        return Pages(ch.id, ch.number, ch.name, list)

