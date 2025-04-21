from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class LionHeartScanProvider(Base):
    name = 'Lion Heart Scan'
    lang = 'pt_Br'
    domain = ['lionheartscan.xyz']

    def __init__(self) -> None:
        self.API = 'https://business-backlion.mu4irv.easypanel.host/manga'
    
    def getManga(self, link: str) -> Manga:
        id = link.split('/')
        response = Http.get(f'{self.API}/{id[4]}').json()
        return Manga(link, response['titulo'])

    def getChapters(self, id: str) -> List[Chapter]:
        id_parts = id.split('/')
        chapters_data = Http.get(f'{self.API}/{id_parts[4]}/capitulos').json()
        response = Http.get(f'{self.API}/{id_parts[4]}').json()
        title = response['titulo']
        chapters_list = []
        
        for chapter in chapters_data:
            pages = chapter['paginas']
            chapter_title = chapter['titulo']
            chapters_list.append(Chapter(pages, chapter_title, title))
        
        return chapters_list
    
    def getPages(self, ch: Chapter) -> Pages:
        list = []
        for pgs in ch.id:
            list.append(pgs)
        return Pages(ch.id, ch.number, ch.name, list)

