from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class BloggerCms(Base):

    def __init__(self) -> None:
        self.get_title = 'header h1'
        self.API_domain = 'www.strellascan.xyz'
        self.get_pages = 'div.separator a img'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one(self.get_title)

        return Manga(link, title.get_text(strip=True))

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one(self.get_title)
        response = Http.get(f'https://{self.API_domain}/feeds/posts/default/-/{title.get_text(strip=True)}?alt=json&start-index=1&max-results=150').json()
        list = []
        for ch in response['feed']['entry']:
            if ch['link'][4]['href'] == id:
                continue
            list.append(Chapter(ch['link'][4]['href'], ch['title']['$t'], title.get_text(strip=True)))
        return list
     
    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        get_images = soup.select(self.get_pages)
        list = []
        for img in get_images:
            list.append(img.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)