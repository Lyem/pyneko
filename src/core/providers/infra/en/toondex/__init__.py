from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class ToonDexProvider(Base):
    name = 'Toon Dex'
    lang = 'en'
    domain = ['toondex.net']

    def __init__(self) -> None:
        self.base = 'https://toondex.net'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div h1.text-2xl.font-semibold')

        return Manga(link, title.get_text(strip=True))

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div h1.text-2xl.font-semibold')
        get_chapters = soup.select('div#chapters-box a')
        list = []
        for ch in get_chapters:
            number = ch.select_one('div.font-medium')
            list.append(Chapter(f'{self.base}{ch.get('href')}', number.get_text(strip=True), title.get_text(strip=True)))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        get_pages = soup.select('img.mx-auto.w-full')
        list = []
        for pgs in get_pages:
            src = pgs.get('src') or pgs.get('data-src')
            if src:
                list.append(src)
        return Pages(ch.id, ch.number, ch.name, list)

