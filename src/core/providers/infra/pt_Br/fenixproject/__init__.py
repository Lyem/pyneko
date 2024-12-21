import re
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.__seedwork.infra.http.contract.http import Response
from core.providers.domain.entities import Chapter, Pages, Manga
from core.providers.infra.template.wordpress_madara import WordPressMadara
from urllib.parse import urljoin, urlencode, urlparse, urlunparse, parse_qs

class FenixProjectProvider(WordPressMadara):
    name = 'Fenix Project'
    lang = 'pt-Br'
    domain = ['fenixproject.site']

    def __init__(self):
        self.url = 'https://fenixproject.site/'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'

    def getPages(self, ch: Chapter) -> Pages:
        try:
            uri = urljoin(self.url, ch.id)
            uri = self._add_query_params(uri, {'style': 'paged'})
            response = Http.get(uri, timeout=getattr(self, 'timeout', None))
            soup = BeautifulSoup(response.content, 'html.parser')
            data = soup.select_one('script#chapter_preloaded_images')
            pattern = r'https:\\/\\/[^\"]+'
            links = re.findall(pattern, data.get_text(strip=True))
            links = [link.replace('\\/', '/') for link in links]
            # print(links)
            list = []
            list.extend(links)
            number = re.findall(r'\d+\.?\d*', str(ch.number))[0]
            return Pages(ch.id, number, ch.name, list)
        except Exception as e:
            print(e)
