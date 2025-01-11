from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class XZScanlatorProvider(Base):
    name = 'XZ Scanlator'
    lang = 'pt_Br'
    domain = ['xzscanlator.blogspot.com']

    def __init__(self) -> None:
        pass
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('header  h1')

        return Manga(link, title.get_text(strip=True))

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('header  h1')
        response = Http.get(f'https://xzscanlator.blogspot.com/feeds/posts/default/-/{title.get_text(strip=True)}.?alt=json&start-index=1&max-results=9999').json()
        list = []
        for ch in response['feed']['entry']:
            if ch['link'][4]['href'] == id:
                continue
            list.append(Chapter(ch['link'][4]['href'], ch['link'][4]['title'], title.get_text(strip=True)))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        get_pages = soup.select('div.check-box div.separator a')
        list = []
        for pages in get_pages:
            list.append(pages.get('href'))
        return Pages(ch.id, ch.number, ch.name, list)

