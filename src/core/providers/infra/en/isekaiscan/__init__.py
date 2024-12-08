import re
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Chapter, Pages
from core.providers.infra.template.wordpress_madara import WordPressMadara
from urllib.parse import urljoin, urlencode, urlparse, urlunparse, parse_qs

class IsekaiScanProvider(WordPressMadara):
    name = 'Isekai Scans'
    lang = 'en'
    domain = ['www.isekaiscan.top']

    def __init__(self):
        self.url = 'https://www.isekaiscan.top'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'p#arraydata'
        self.query_title_for_uri = 'div.post-title h1'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'

    def _get_chapters_ajax(self, manga_id):
        if not manga_id.endswith('/'):
            manga_id += '/'
        response = Http.get(manga_id)
        soup = BeautifulSoup(response.content, 'html.parser')
        id = soup.select_one('input.rating-post-id')
        uri = urljoin(self.url, f'ajax-list-chapter?mangaID={id.get('value')}')
        response = Http.get(uri)
        data = self._fetch_dom(response, self.query_chapters)
        if data:
            return data
        else:
            raise Exception('No chapters found (new ajax endpoint)!')
        
    def getPages(self, ch: Chapter) -> Pages:
        try:
            response = Http.get(ch.id)
            soup = BeautifulSoup(response.content, 'html.parser')
            get_pages = soup.select_one('p#arraydata')
            list = get_pages.get_text(strip=True).split(',')
            return Pages(ch.id, ch.number, ch.name, list)
        except Exception as e:
            print(e)