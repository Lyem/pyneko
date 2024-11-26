from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class AgrComicsProvider(Base):
    name = 'Agr Comics'
    lang = 'en'
    domain = ['agrcomics.com']

    def __init__(self) -> None:
        self.base = 'https://agrcomics.com'
        self.cdn = 'https://cdn.meowing.org/uploads/'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div h1.font-bold')

        return Manga(link, title.get_text().strip())

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div h1.font-bold')
        get_chapters_div = soup.select_one('div#chapters')
        chapters = get_chapters_div.select('a')
        list = []
        for ch in chapters:
            number = ch.select_one('span.text-sm.truncate')
            list.append(Chapter(f'{self.base}{ch.get('href')}', number.get_text().strip(), title.get_text().strip()))
        return list
    
    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.select_one('div#pages')
        image = images.select('img')
        list = []
        for img in image:
            uid = img.get("uid")
            list.append(f'{self.cdn}{uid}')
        return Pages(ch.id, ch.number, ch.name, list)


