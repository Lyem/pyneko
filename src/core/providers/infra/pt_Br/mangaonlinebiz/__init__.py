from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class MangaOnlineBizProvider(Base):
    name = 'Manga Online'
    lang = 'pt_Br'
    domain = ['mangaonline.biz']

    def __init__(self) -> None:
        pass
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div.data > h1')
        return Manga(link, title.get_text(strip=True))

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div.data > h1')
        get_chapters = soup.select('ul.episodios a')
        list = []
        for ch in get_chapters:
            number = " ".join(ch.get_text().split(" ")[:2])
            list.append(Chapter(ch.get('href'), number, title.get_text(strip=True)))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        get_pages = soup.select('div.content p > img')
        list = []
        for pages in get_pages:
            list.append(pages.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)
