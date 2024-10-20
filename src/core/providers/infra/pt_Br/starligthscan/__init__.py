from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class StarLightScanProvider(Base):
    name = 'Star Ligth Scan'
    lang = 'pt-Br'
    domain = ['starligthscan.com']

    def __init__(self) -> None:
        self.base = 'https://starligthscan.com'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('.mangaDetails__title').text
        return Manga(link, title)

    def getChapters(self, link: str) -> List[Chapter]:
        list = []
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        chapters = soup.select_one('.mangaDetails__episodesContainer').select('a')
        title = soup.select_one('.mangaDetails__title').text
        for chapter in chapters:
            text = chapter.get_text(strip=True)
            if not link.endswith('/'):
                link += '/'
            href = f"{link}{chapter.get('href')}"
            list.append(Chapter(href, text, title))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        list = []
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        imgs = soup.select_one('.scanImagesContainer').select('img')
        for img in imgs:
            list.append(img.get('data-src'))
        
        return Pages(ch.id, ch.number, ch.name, list)
