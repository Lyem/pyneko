import nodriver as uc
from typing import List
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Chapter
from core.providers.infra.template.wordpress_madara import WordPressMadara
from core.cloudflare.application.use_cases import IsCloudflareBlockingUseCase

class MiniTwoScanProvider(WordPressMadara):
    name = 'MiniTwo Scan'
    lang = 'pt_Br'
    domain = ['minitwoscan.com']

    def __init__(self):
        self.url = 'https://minitwoscan.com'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break.no-gaps'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'
    
    def _get_chapters_ajax_old(self, data_id, id, background):
        content= ''
        async def get_script_result():
            nonlocal content
            browser = await uc.start(
                browser_args=[
                    '--window-size=600,600', 
                    f'--app={id}',
                    '--disable-extensions', 
                    '--disable-popup-blocking'
                ],
                browser_executable_path=None,
                headless=background
            )
            page = await browser.get(id)
            while(True):
                page_content = await page.get_content()
                if IsCloudflareBlockingUseCase().execute(page_content):
                    sleep(1)
                else:
                    break
            fetch_content = await page.evaluate('''fetch("https://minitwoscan.com/wp-admin/admin-ajax.php", {
                "credentials": "include",
                "headers": {
                    "Accept": "*/*",
                    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                    "Alt-Used": "minitwoscan.com",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache"
                },
                "referrer": "https://minitwoscan.com/manga/lixo/",
                "body": "action=manga_get_chapters&manga=''' + data_id + '''",
                "method": "POST",
                "mode": "cors"
            }).then(response => response.text());''', await_promise=True)
            soup = BeautifulSoup(fetch_content, 'html.parser')
            data = soup.select(self.query_chapters)
            if data:
                content = data
            else:
                browser.stop()

            browser.stop()
        uc.loop().run_until_complete(get_script_result())
        return content
    
    def getChapters(self, id: str) -> List[Chapter]:
        uri = urljoin(self.url, id)
        response = Http.get(uri)
        soup = BeautifulSoup(response.content, 'html.parser')
        data = soup.select(self.query_title_for_uri)
        element = data.pop()
        title = element['content'].strip() if 'content' in element.attrs else element.text.strip()
        dom = soup.select('body')[0]
        data = dom.select(self.query_chapters)
        placeholder = dom.select_one(self.query_placeholder)
        if placeholder:
            try:
                data = self._get_chapters_ajax(id)
            except Exception:
                try:
                    data = self._get_chapters_ajax_old(placeholder['data-id'], id, False)
                except Exception:
                    pass

        chs = []
        for el in data:
            ch_id = self.get_root_relative_or_absolute_link(el, uri)
            ch_number = el.text.strip()
            ch_name = title
            chs.append(Chapter(ch_id, ch_number, ch_name))

        chs.reverse()
        return chs