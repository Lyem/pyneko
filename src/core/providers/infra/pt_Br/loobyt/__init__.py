import re
import asyncio
import nodriver as uc
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from urllib.parse import urlparse, parse_qs
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class LoobytProvider(Base):
    name = 'Loobyt'
    lang = 'pt_Br'
    domain = [re.compile(r"^(?:[a-zA-Z0-9-]+\.)*loobyt\.com$")]

    def __init__(self) -> None:
        self.base = 'https://www.loobyt.com/readme/'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1.hidden.text-3xl.font-bold')

        return Manga(link, title.get_text(strip=True))

    def getChapters(self, id: str) -> List[Chapter]:
        try:
            response = Http.get(id)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.select_one('h1.hidden.text-3xl.font-bold')
            get_id = soup.select_one('div.flex.items-center.justify-between a')
            url_parsed = urlparse(get_id.get('href'))
            params = parse_qs(url_parsed.query)
            id = params.get('pull', [None])[0]
            response = Http.get('https://www.loobyt.com/api/deprecated/chapter.publicAllChapters?batch=1&input={"0":{"json":{"id":'+ f'"{id}"' +',"page":1,"limit":999999999999,"sort":"desc","search":""}}}').json()
            list = []
            for ch in response[0]['result']['data']['json']['chapters']:
                list.append(Chapter(f'{self.base}{ch['id']}', f'Capítulo {ch['number']}', title.get_text(strip=True)))
            return list
        except Exception as e:
            print(e)

    # def get_Pages(self, id, sleep, background=False):
    #     async def get_Pages_driver():
    #         browser = await uc.start(
    #             browser_args=[
    #                 '--window-size=600,600',
    #                 f'--app={id}',
    #                 '--disable-extensions',
    #                 '--disable-popup-blocking'
    #             ],
    #             browser_executable_path=None,
    #             headless=background
    #         )
    #         page = await browser.get(id)
    #         await asyncio.sleep(sleep)
    #         html = await page.get_content()
            
    #         # Parse do HTML para extrair scripts
    #         soup = BeautifulSoup(html, 'html.parser')
    #         scripts = soup.find_all('script')
    #         scripts_text = '\n'.join(script.text for script in scripts)
            
    #         # Regex para encontrar URLs de imagens (igual ao Kotlin)
    #         IMAGE_URL_REGEX = re.compile(r'url\\\":\\\"([^\\\\\"]+)')
    #         matches = IMAGE_URL_REGEX.findall(scripts_text)
            
    #         browser.stop()
    #         return [match for match in matches]  # Retorna lista de URLs

    #     resultado = uc.loop().run_until_complete(get_Pages_driver())
    #     return resultado

    def getPages(self, ch: Chapter) -> Pages:
        try:
            # response = self.get_Pages(ch.id, 10)
            response = Http.get(ch.id)
            soup = BeautifulSoup(response.content, 'html.parser')
            scripts = soup.find_all('script')
            scripts_text = '\n'.join(script.text for script in scripts)
            
            # Regex para encontrar URLs de imagens (igual ao Kotlin)
            IMAGE_URL_REGEX = re.compile(r'url\\\":\\\"([^\\\\\"]+)')
            matches = IMAGE_URL_REGEX.findall(scripts_text)
            list = [match for match in matches]
            # soup = BeautifulSoup(response, 'html.parser')
            # scripts = soup.select('body script')[13]
            # cdn_pattern = r'https:\/\/cdn\.readmangas\.org\/[^"]+'
            # list = re.findall(cdn_pattern, scripts.get_text())
            # urls = [url.rstrip("\\") for url in list]
            return Pages(ch.id, ch.number, ch.name, list)
        except Exception as e:
            print(e)
