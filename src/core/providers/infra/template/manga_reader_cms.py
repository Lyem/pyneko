import base64
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from urllib.parse import unquote, urljoin, urlparse
from core.providers.domain.entities import Chapter, Pages, Manga

class MangaReaderCms(Base):
    def __init__(self):
        super().__init__()
        self.url = None
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'ul.chapters li h5.chapter-title-rtl'
        self.query_pages = 'div#all source.img-responsive'
        self.query_title_for_uri = 'h1.entry-title'

    def fetch_dom(self, response, query):
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.select(query)

    def get_relative_link(self, element):
        return element['href']

    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        uri = urlparse(link)
        id = uri.path + '?' + uri.query if uri.query else uri.path
        data = self.fetch_dom(response, self.query_title_for_uri)
        return Manga(id=id, name=data[0].text.strip())

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(urljoin(self.url, id))
        data = self.fetch_dom(response, self.query_chapters)
        title = self.fetch_dom(response, self.query_title_for_uri)[0].text.strip()
        chapters = []
        for element in data:
            anchor = element if element.name == 'a' else element.select_one('a')
            chapters.append(Chapter(
                id=self.get_relative_link(anchor),
                number=element.select('span.chapternum')[0].text,
                name=title
            ))
        chapters.reverse()
        return chapters

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(urljoin(self.url, ch.id))
        data = self.fetch_dom(response, self.query_pages)
        pages = []
        for element in data:
            try:
                src = element['data-src'].split('://').pop()
                pages.append(unquote(base64.b64decode(src or '').decode('utf-8')))
            except Exception:
                src = (element.get('data-src') or element['src']).strip()
                pages.append(urljoin(response.url, src))
        return Pages(id=ch.id, number=ch.number, name=ch.name, pages=pages)