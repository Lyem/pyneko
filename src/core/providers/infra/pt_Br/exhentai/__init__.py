from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class ExHentaiProvider(Base):
    name = 'ExHentai'
    lang = 'pt_Br'
    domain = ['exhentai.net.br']

    def __init__(self) -> None:
        pass
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div.stats_box > h3')

        return Manga(link, title.get_text().strip())

    def getChapters(self, id: str) -> List[Chapter]:
        courrent_page = 1
        list = []
        while True:
            response = Http.get(f'{id}/page/{courrent_page}/')
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.select_one('div.stats_box > h3')
            chapter_div = soup.select_one('div.chapters_l')
            chapters = chapter_div.select('div.chapter_content > a')
            get_pagination = chapter_div.select_one('ul.content-pagination')
            for ch in chapters:
                number = ch.select_one('div.name_chapter > span')
                list.append(Chapter(ch.get('href'), f'Capítulo {number.get_text().strip()}', title.get_text().strip()))
            if get_pagination:
                courrent_page += 1
            else: 
                break
        return list
            
    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        pages_div = soup.select_one('div.reader_list')
        pages = pages_div.select('noscript > img')
        list = []
        for pg in pages:
            list.append(pg.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)