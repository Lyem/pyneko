import re
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class MangaBrProvider(Base):
    name = 'Manga Br'
    lang = 'pt_Br'
    domain = ['mangabr.net']

    def __init__(self) -> None:
        self.base = 'https://mangabr.net'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div > h1.mb-0.d-inline-block.h2')

        return Manga(link, title.get_text().strip())
    
    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div > h1.mb-0.d-inline-block.h2')
        get_chapters_div = soup.select_one('div.row.list-books')
        get_chapters = get_chapters_div.select('div.col-chapter > a')
        list = []
        for ch in get_chapters:
            number = ch.select_one('h5.mb-0')
            if number:
                number_text = number.get_text().strip()
                number_text = re.sub(r'\d{2}-\d{2}-\d{4}', '', number_text).strip()
                number_text = re.sub(r'\s+', ' ', number_text)
                list.append(Chapter(f'{self.base}{ch.get("href")}', number_text, title.get_text().strip()))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        list = []
        courrent_page = 1
        while True:
            response = Http.get(f'{ch.id}/{courrent_page}')
            soup = BeautifulSoup(response.content, 'html.parser')
            image = soup.select_one('div.book-page > img.img-fluid')
            button_next = soup.select_one('a.btn-next')
            list.append(image.get('src'))
            if button_next:
                courrent_page += 1
            else:
                break
        return Pages(ch.id, ch.number, ch.name, list)