from typing import List
from bs4 import BeautifulSoup
from urllib.parse import quote
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class FenixManhwasProvider(Base):
    name = 'Fênix Manhwas'
    lang = 'pt_Br'
    domain = ['fenixcomicsbr.blogspot.com']

    def __init__(self) -> None:
        pass
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1.my-2.text-2xl.line-clamp-2.text-gray-900')
        return Manga(link, title.get_text().strip())

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1.my-2.text-2xl.line-clamp-2.text-gray-900')
        if title is None:
            raise Exception("Title not found in the page")

        encoded_title = quote(title.get_text().strip())
        response = Http.get(f'https://fenixcomicsbr.blogspot.com/feeds/posts/default/-/{encoded_title}?alt=json&start-index=1&max-results=150').json()

        if 'entry' not in response['feed']:
            encoded_title = quote(title.get_text().strip().lower())
            response = Http.get(f'https://fenixcomicsbr.blogspot.com/feeds/posts/default/-/{encoded_title}?alt=json&start-index=1&max-results=150').json()
            
        list = []
        for ch in response['feed']['entry']:
            if len(ch['link']) > 4 and ch['link'][4]['href'] != id:
                list.append(Chapter(ch['link'][4]['href'], ch['link'][4]['title'], title.get_text().strip()))

        return sorted(list, key=lambda ch: ch.number)

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.select_one('article#reader')
        image = images.select('div.separator > a > img')
        list = []
        for img in image:
            list.append(img.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)

