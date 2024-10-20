import re
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Chapter, Pages, Manga

class MangaBrProvider(Base):
    name = 'Manga br'
    lang = 'pt-Br'
    domain = ['mangabr.net']

    def __init__(self) -> None:
        self.base = 'https://mangabr.net'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1.h2')
        return Manga(link, title.getText())

    def getChapters(self, link: str) -> List[Chapter]:
        list = []
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1.h2')
        chs_base = soup.select_one('div.list-books')
        chs = chs_base.select('a')
        for chapter in chs:
            ch = chapter.select_one('h5')
            for div in ch.find_all('div'):
                div.decompose()
            list.append(Chapter(f'{self.base}{chapter.get('href')}', ' '.join(str(ch.getText()).split()), title.getText()))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        pages_list = []
        response = Http.get(ch.id)
        
        while True:
            soup = BeautifulSoup(response.content, 'html.parser')
            img = soup.select_one('div.book-page > img')
            
            if img:
                pages_list.append(img.get('src'))
            
            next_button = soup.select_one('a.btn-next')
            
            if next_button and next_button.get('href'):
                next_url = f"{self.base}{next_button.get('href')}"
                response = Http.get(next_url)
            else:
                break
        
        return Pages(ch.id, ch.number, ch.name, pages_list)
