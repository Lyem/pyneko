from fake_useragent import UserAgent
from core.providers.domain.entities import Pages
from core.download.application.use_cases import DownloadUseCase
from core.providers.infra.template.wordpress_etoshore_manga_theme import WordpressEtoshoreMangaTheme

class NextScanProvider(WordpressEtoshoreMangaTheme):
    name = 'Next Scan'
    lang = 'pt_Br'
    domain = ['nextscan.cloud']

    def __init__(self) -> None:
        self.url = 'https://nextscan.cloud'
        self.get_title = 'h1'
        self.get_chapters_list = 'div.list-box.chapter-list'
        self.chapter = 'li.language-br a'
        self.get_chapter_number = 'div.title'
        self.get_div_page = 'div.chapter-image-content'
        self.get_pages = 'div.chapter-item > img'

        ua = UserAgent()
        user = ua.chrome
        self.headers = {'host': 'nextscan.cloud', 'user_agent': user, 'referer': f'{self.url}/series'}

    # def download(self, pages: Pages, fn: any, headers=None, cookies=None):
    #     if headers is not None:
    #         headers = headers | self.headers
    #     else:
    #         headers = self.headers
    #     return DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)