import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fake_useragent import UserAgent
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Pages
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Chapter, Pages, Manga
from core.providers.infra.template.wordpress_madara import WordPressMadara

class HuntersScanProvider(WordPressMadara):
    name = 'Hunters scan'
    lang = 'pt-Br'
    domain = ['hunterscomics.com']

    def __init__(self):
        self.url = 'https://hunterscomics.com'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break.no-gaps'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'
        ua = UserAgent()
        user = ua.chrome
        self.headers = {'host': 'hunterscomics.com', 'user_agent': user, 'referer': f'{self.url}/series', 'Cookie': 'acesso_legitimo=1'}
        self.timeout=3

    def getPages(self, ch: Chapter) -> Pages:
        try:
            request = Http.get(ch.id)
            # print(f'[no-render] {request.content}')
            soup = BeautifulSoup(request.content, 'html.parser')
            # get_div_images = soup.select(self.query_pages)
            # print('pegou1')
            get_images = soup.select(f'{self.query_pages} img')
            list = []
            # print('list')
            for img in get_images:
                images = img.get('data-src')
                list.append(images.split('=')[1])
        except Exception as e:
            print(e)
            list = []
        return Pages(ch.id, ch.number, ch.name, list)
    
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        if headers is not None:
            headers = headers | self.headers
        else:
            headers = self.headers
        return DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies, timeout=self.timeout)