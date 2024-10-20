from bs4 import BeautifulSoup
from urllib.parse import urljoin
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Chapter, Pages
from core.providers.infra.template.manga_reader_cms import MangaReaderCms

class SeitaCelestialProvider(MangaReaderCms):
    name = 'Seita Celestial'
    lang = 'pt-Br'
    domain = ['seitacelestial.com']

    def __init__(self):
        super().__init__()
        self.url = 'https://seitacelestial.com'
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'div#chapterlist ul li'
        self.query_pages = 'div#readerarea img'
        self.query_title_for_uri = 'h1.entry-title'
    
    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(urljoin(self.url, ch.id))
        soup = BeautifulSoup(response.content, 'html.parser')
        link_tag = soup.find('link', {'rel': 'alternate', 'title': 'JSON'})
        url = link_tag.get('href')
        request = Http.get(url)
        data = request.json()
        soup = BeautifulSoup(data['content']['rendered'], 'html.parser')
        img_tags = soup.find_all('img')
        pages = []
        for url in img_tags:
            pages.append(url.get('src').strip())
        return Pages(id=ch.id, number=ch.number, name=ch.name, pages=pages)