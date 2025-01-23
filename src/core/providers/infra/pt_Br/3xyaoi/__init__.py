from urllib.parse import urljoin, urlencode, urlparse, urlunparse, parse_qs
from core.providers.infra.template.wordpress_madara import WordPressMadara
from core.providers.domain.entities import Chapter, Pages
from core.__seedwork.infra.http import Http
from bs4 import BeautifulSoup
import re

class XXXYaoiProvider(WordPressMadara):
    name = '3xyaoi'
    lang = 'pt-Br'
    domain = ['3xyaoi.com']

    def __init__(self):
        self.url = 'https://3xyaoi.com'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break'
        self.query_title_for_uri = 'div.post-title > h1'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'

    def getPages(self, ch: Chapter) -> Pages:
        try:
            uri = urljoin(self.url, ch.id)
            uri = self._add_query_params(uri, {'style': 'list'})
            response = Http.get(uri, timeout=getattr(self, 'timeout', None))
            soup = BeautifulSoup(response.content, 'html.parser')
            data = soup.select(self.query_pages)
            if not data:
                uri = self._remove_query_params(uri, ['style'])
                response = Http.get(uri, timeout=getattr(self, 'timeout', None))
                soup = BeautifulSoup(response.content, 'html.parser')
                data = soup.select(self.query_pages)
            list = [] 
            for el in data:
                list.append(self._process_page_element(el, uri))

            # number = re.findall(r'\d+\.?\d*', str(ch.number))[0]
            
            return Pages(ch.id, ch.number, ch.name, list)
        except Exception as e:
            print(e)