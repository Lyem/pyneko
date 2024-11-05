import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Chapter, Pages
from core.providers.infra.template.manga_reader_cms import MangaReaderCms

class CartelDeManhwasProvider(MangaReaderCms):
    name = 'Cartel De Manhwas'
    lang = 'es'
    domain = ['carteldemanhwas.com']

    def __init__(self):
        super().__init__()
        self.url = 'https://carteldemanhwas.com'
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'div#chapterlist ul li'
        self.query_pages = 'div#readerarea img'
        self.query_title_for_uri = 'h1.entry-title'
    
    def getPages(self, ch: Chapter) -> Pages:
        list = []
        response = Http.get(urljoin(self.url, ch.id))
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.select('script')
        image_regex = r'"images":\[(.*?)\]'
        for script in scripts:
            content = script.get_text()
            if 'ts_reader.run' in content:
                match = re.search(image_regex, script.string)
                if match:
                    images_str = match.group(1).replace('\\/', '/')
                    images = [img.strip().strip('"') for img in images_str.split(',')]
                    list = images
                break
        return Pages(ch.id, ch.number, ch.name, list)