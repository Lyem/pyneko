import re
import nodriver as uc
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Chapter, Pages
from core.providers.infra.template.manga_reader_cms import MangaReaderCms
from core.config.login_data import insert_login, LoginData, get_login, delete_login

class YomuComicsProvider(MangaReaderCms):
    name = 'Yomu Comics'
    lang = 'pt-Br'
    domain = ['yomucomics.com']
    has_login = True

    def __init__(self):
        super().__init__()
        self.url = 'https://yomucomics.com'
        self.path = '/'
        self.login_page = 'https://yomucomics.com/login/'
        self.domain = 'yomucomics.com'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'div#chapterlist ul li'
        self.query_pages = 'div#readerarea img'
        self.query_title_for_uri = 'h1.entry-title'

    def _is_login_page(self, html) -> bool:
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string if soup.title else ""
        if "Acessar ‹ YomuComics — WordPress" in title:
            return True
        
        return False
    
    def login(self):
        login_info = get_login(self.domain)
        if login_info:
            response  = Http.get(self.url)
            if self._is_login_page(response.content):
                delete_login(self.domain)
                login_info = None
            
        if not login_info:
            async def getLogin():
                browser = await uc.start()
                page = await browser.get(self.login_page)
                while True:
                    html_page = await page.get_content()
                    if self._is_login_page(html_page):
                        sleep(1)
                    else:
                        cookies = await browser.cookies.get_all()
                        for cookie in cookies:
                            if cookie.name.startswith('wordpress_logged_in_'):
                                dynamic_cookie_name = cookie.name
                                dynamic_cookie_value = cookie.value
                                insert_login(LoginData(self.domain, {}, {dynamic_cookie_name: cookie.value}))
                                break
                        break
                browser.stop()
            uc.loop().run_until_complete(getLogin())

    
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