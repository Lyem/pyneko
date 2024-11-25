from core.__seedwork.infra.http import Http
from core.providers.infra.template.wordpress_madara import WordPressMadara
from urllib.parse import urljoin, urlencode, urlparse, urlunparse, parse_qs

class AdultWebToonProvider(WordPressMadara):
    name = 'Adult Web Toon'
    lang = 'en'
    domain = ['adultwebtoon.com']

    def __init__(self):
        self.url = 'https://adultwebtoon.com'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'ul#chapters-list > li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break.no-gaps'
        self.query_title_for_uri = 'div.post-title > h1'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'
    
    def _get_chapters_ajax_old(self, data_id):
        uri = urljoin(self.url, f'{self.path}/wp-admin/admin-ajax.php')
        response = Http.post(uri, data=f'action=ajax_chap&post_id={data_id}', headers={
            'content-type': 'application/x-www-form-urlencoded',
            'x-referer': self.url
        }, timeout=getattr(self, 'timeout', None))
        data = self._fetch_dom(response, self.query_chapters)
        if data:
            return data
        else:
            raise Exception('No chapters found (old ajax endpoint)!')