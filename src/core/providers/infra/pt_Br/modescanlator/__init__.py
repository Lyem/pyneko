from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class ModeScanlatorProvider(Base):
    name = 'Mode Scanlator'
    lang = 'pt-Br'
    domain = ['site.modescanlator.net']

    def __init__(self) -> None:
        self.api = 'https://api.modescanlator.net'
        self.reader = 'https://site.modescanlator.net/series/'
    
    def getManga(self, link: str) -> Manga:
        if link.endswith('/'):
            link = link[:-1]
        id = link.split("/").pop();
        response = Http.get(f'{self.api}/query?adult=true&page=1&perPage=999999999999999999')
        data = response.json()
        for manga in data['data']:
            if manga['series_slug'] == id:
                return Manga(manga['id'], manga['title'])
        

    def getChapters(self, id: str) -> List[Chapter]:
        manga_response = Http.get(f'{self.api}/query?adult=true&page=1&perPage=999999999999999999')
        manga_data = manga_response.json()
        response = Http.get(f'{self.api}/chapter/query?page=1&perPage=999999999999999999&series_id={id}')
        data = response.json()
        list = []
        name = ''
        for manga in manga_data['data']:
            if manga['id'] == id:
                name = manga['title']
        for chapter in data['data']:
            list.append(Chapter(f'{chapter['series']['series_slug']}/{chapter['chapter_slug']}',chapter['chapter_name'], name))
        list.reverse()
        return list
    
    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(f'{self.reader}{ch.id}')
        soup = BeautifulSoup(str(response.content), 'html.parser')
        imgs = soup.select('div.flex.flex-col.justify-center.items-center > img')
        list = []
        for img in imgs:
            if img.get('src'):
                if img.get('src') != '/icon.png':
                    list.append(img.get('src'))
            else: 
                list.append(img.get('data-src'))
        return Pages(ch.id, ch.number, ch.name, list)