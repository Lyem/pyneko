from core.providers.infra.template.wordpress_madara import WordPressMadara
from core.__seedwork.infra.http import Http
from urllib.parse import urljoin
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Pages

class MoonLoversScanProvider(WordPressMadara):
    name = 'Moon lovers scan'
    lang = 'pt-Br'
    domain = ['moonloversscan.com.br']

    def __init__(self):
        self.url = 'https://moonloversscan.com.br'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter.has-thumb > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'
    
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        if headers is not None:
            headers = headers | {'Referer': 'https://moonloversscan.com.br/lixo'}
        else:
            headers = {'Referer': 'https://moonloversscan.com.br/lixo'}
        return DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)
    
    def _get_chapters_ajax(self, manga_id):
        uri = urljoin(self.url, f'{manga_id}ajax/chapters/')
        response = Http.post(uri, headers={'Cookie': 'visited=true; wpmanga-reading-history=W3siaWQiOjg4MiwiYyI6IjIzMzU5IiwicCI6MSwiaSI6IiIsInQiOjE3MTk5NjEwODN9XQ%3D%3D'})
        data = self._fetch_dom(response, self.query_chapters)
        if data:
            return data
        else:
            raise Exception('No chapters found (new ajax endpoint)!')