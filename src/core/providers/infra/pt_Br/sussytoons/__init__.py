import re
import asyncio
import nodriver as uc
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
# from urllib.parse import urlparse, parse_qs
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class NewSussyToonsProvider(Base):
    name = 'New Sussy Toons'
    lang = 'pt_Br'
    domain = ['new.sussytoons.site', 'www.sussyscan.com', 'www.sussytoons.site', 'www.sussytoons.wtf']

    def __init__(self) -> None:
        self.base = 'https://api-dev.sussytoons.site'
        self.CDN = 'https://cdn.sussytoons.site'
        self.old = 'https://oldi.sussytoons.site/wp-content/uploads/WP-manga/data/'
        self.oldCDN = 'https://oldi.sussytoons.site/scans/1/obras'
        self.webBase = 'https://www.sussytoons.wtf'
        self.cookies = [{'sussytoons-terms-accepted', 'true'}]
    
    def getManga(self, link: str) -> Manga:
        match = re.search(r'/obra/(\d+)', link)
        id_value = match.group(1)
        response = Http.get(f'{self.base}/obras/{id_value}').json()
        title = response['resultado']['obr_nome']
        return Manga(link, title)

    def getChapters(self, id: str) -> List[Chapter]:
        try:
            match = re.search(r'/obra/(\d+)', id)
            id_value = match.group(1)
            response = Http.get(f'{self.base}/obras/{id_value}').json()
            title = response['resultado']['obr_nome']
            list = []
            for ch in response['resultado']['capitulos']:
                list.append(Chapter([id_value, ch['cap_id'], ], ch['cap_nome'], title))
            return list
        except Exception as e:
            print(e)


    def get_Pages(self, id, sleep, background = False):
        async def get_Pages_driver():
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
            await browser.cookies.set_all(self.cookies)
            await asyncio.sleep(sleep)
            html = await page.get_content()
            browser.stop() 
            return html
        resultado = uc.loop().run_until_complete(get_Pages_driver())
        return resultado
    
    def getPages(self, ch: Chapter) -> Pages:
            try:
                # response = Http.get(f'{self.webBase}/capitulo/{ch.id[1]}')
                # print(f'[no-render]{response.content}')
                list = []
                while_is_true = True
                courrent_page = 0
                sleep_time = 25
                while(while_is_true):
                    html = self.get_Pages(f'{self.webBase}/capitulo/{ch.id[1]}', sleep_time)
                    soup = BeautifulSoup(html, 'html.parser')
                    get_images = soup.select('img.chakra-image.css-8atqhb')
                    for images in get_images:
                        list.append(images.get('src'))
                    if len(list) > 0:
                        while_is_true = False

                    if courrent_page >= 3:
                        break
                    courrent_page += 1

                    sleep_time += 5

                return Pages(ch.id, ch.number, ch.name, list)
            
            except Exception as e:
                print(e)
