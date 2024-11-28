from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class AnteikuScanProvider(Base):
    name = 'AnteikuScans'
    lang = 'fr'
    domain = ['anteikuscan.fr']

    def __init__(self) -> None:
        self.base = 'https://anteikuscan.fr'
        self.CDN = 'https://cdn.meowing.org/uploads/'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('head meta[property="og:title"]')

        return Manga(link, title.get('content').strip())

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('head meta[property="og:title"]')
        chapters = soup.select('div#chapters > a')
        list = []
        for ch in chapters:
            number = ch.select_one('span.text-sm.truncate')
            list.append(Chapter(f'{self.base}{ch.get('href')}', number.get_text().strip(), title.get('content').strip()))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        pages = soup.select('div#pages > img')
        list = []
        for pg in pages:
            list.append(f'{self.CDN}{pg.get('uid')}')
        return Pages(ch.id, ch.number, ch.name, list)

