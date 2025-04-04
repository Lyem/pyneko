from fake_useragent import UserAgent
from core.providers.domain.entities import Pages
from core.download.application.use_cases import DownloadUseCase
from core.providers.infra.template.wordpress_madara import WordPressMadara

class SerpentesComicsProvider(WordPressMadara):
    name = 'Serpentes Comics'
    lang = 'pt_Br'
    domain = ['serpentescomics.com.br']

    def __init__(self):
        self.url = 'https://serpentescomics.com.br'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break.no-gaps'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'


        ua = UserAgent()
        user = ua.chrome
        self.headers = {'host': 'serpentescomics.com.br', 'user_agent': user, 'referer': f'{self.url}/series'}

    
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        if headers is not None:
            headers = headers | self.headers
        else:
            headers = self.headers
        return DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)