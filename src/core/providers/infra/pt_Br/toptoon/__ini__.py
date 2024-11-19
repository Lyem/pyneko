import nodriver as uc
from time import sleep
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga
from core.config.login_data import insert_login, LoginData, get_login, delete_login

class BlackoutProvider(Base):
    name = 'Blackout/TopToon'
    lang = 'pt_Br'
    domain = ['toptoon.com.co']
    has_login = True
    
    def __init__(self) -> None:
        self.login_page = 'https://toptoon.com.co/temp/login'
        self.url = 'https://toptoon.com.co'
        self.domain = 'toptoon.com.co'

    def _is_login_page(self, html) -> bool:
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string if soup.title else ""
        if "Blackout Comics | Aviso" in title:
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
                            if cookie.name == 'blackoutcomics_session':
                                insert_login(LoginData(self.domain, {}, {'blackoutcomics_session': cookie.value}))
                                break
                        break
                browser.stop()
            uc.loop().run_until_complete(getLogin())

    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        div_title = soup.select_one('div.trailer-content')
        title = div_title.select('h2')[1]
        return Manga(link, title.get_text().strip())

    def getChapters(self, link: str) -> List[Chapter]:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        div_title = soup.select_one('div.trailer-content')
        title = div_title.select('h2')[1].get_text().strip()
        div_caps = soup.select_one('div#capitulosList')
        caps = div_caps.select('h5')
        list = []
        for cap in caps:
            a = cap.select('a')[1]
            list.append(Chapter(a.get('href'), a.get_text().strip(), title))
        list.reverse()
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        imgs_div = soup.select_one('div.img-capitulos')
        imgs = imgs_div.select('canvas')
        list = []
        for img in imgs:
            for _, value in img.attrs.items():
                if isinstance(value, str) and value.endswith('.webp'):
                    list.append(f'{self.url}{value}')
                    break
        return Pages(ch.id, ch.number, ch.name, list)

