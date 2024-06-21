from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class StarLightScanProvider(Base):
    name = 'Star Ligth Scan'
    icon = 'https://i.imgur.com/QRjE79s.png'
    icon_hash = 'd/iFDQIoqraAa360R1NPCZWlHiugekWiJw'
    lang = 'pt-Br'
    domain = 'starligthscan.com'

    def __init__(self) -> None:
        self.base = 'https://starligthscan.com'
    
    def getMangas(self) -> List[Manga]:
        list = []
        n = 0
        while True:
            n += 1
            response = Http.get(f'{self.base}/mangas/?page-current={n}')
            soup = BeautifulSoup(response.content, 'html.parser')
            mangas = soup.select_one('#allMangasList').select('a')
            for manga in mangas:
                text = manga.get_text(strip=True)
                href = manga.get('href')
                list.append(Manga(href, text))
            button = soup.select_one('footer.base__horizontalList.base__horizontalList--center').select('a')[1]
            if button.has_attr('disabled'):
                break
        return list
    
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
