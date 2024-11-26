from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class ApenasUmaFaProvider(Base):
    name = 'Apenas Uma Fã'
    lang = 'pt_Br'
    domain = ['apenasuma-fa.blogspot.com']

    def __init__(self) -> None:
        pass
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1#post-title')
        return Manga(link, title.get_text().strip())
        
    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        slug_div = soup.select_one('div.chapter_get')
        slug = slug_div.get('data-labelchapter')
        title = soup.select_one('h1#post-title')
        response = Http.get(f'https://apenasuma-fa.blogspot.com/feeds/posts/default/-/{slug}?alt=json&start-index=1&max-results=150&orderby=updated').json()
        list = []
        for ch in response['feed']['entry']:
            if ch['link'][4]['href'] != id:
                list.append(Chapter(ch['link'][4]['href'], ch['link'][4]['title'], title.get_text().strip()))
        return sorted(list, key=lambda ch: float(ch.number.split(' ')[1]))

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        pages_div = soup.select_one('div.i_img')
        imgs = pages_div.select('img')
        list = []
        for img in imgs:
            list.append(img.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)