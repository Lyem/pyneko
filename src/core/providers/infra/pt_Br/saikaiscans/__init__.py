import json
import nodriver as uc
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class SaikaiScansProvider(Base):
    name = 'Saikai Scans'
    lang = 'pt_Br'
    domain = ['saikaiscans.net']

    def __init__(self) -> None:
        self.url = 'https://saikaiscans.net/'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1')
        if title.span:
            title.span.decompose()
        return Manga(link, title.get_text(strip=True))
    
    def _exec_js(self, script, background):
        content= ''
        async def get_script_result():
            nonlocal content
            browser = await uc.start(
                browser_args=[
                    '--window-size=600,600', 
                    f'--app=https://google.com',
                    '--disable-extensions', 
                    '--disable-popup-blocking'
                ],
                browser_executable_path=None,
                headless=background
            )
            page = await browser.get('https://google.com')
            await page.evaluate(f'{script}')
            content = await page.evaluate('JSON.stringify(__NUXT__.data[0].story.valueOf().data)')
            browser.stop()
        uc.loop().run_until_complete(get_script_result())
        return content

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find('script', text=lambda t: t and "window.__NUXT__" in t)
        json_content = self._exec_js(script_tag.string, True)
        json_content = json.loads(json_content)
        title = json_content['title']
        chapters = []
        for separator in json_content['separators']:
            for release in separator['releases']:
                chapters.append(Chapter(f'{self.url}ler/comics/{json_content['slug']}/{release['id']}/{release['slug']}', release['chapter'], title))      
        return chapters

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        div = soup.select_one('div#comic-pages')
        imgs = div.select('img')
        list = []
        for img in imgs:
            list.append(img.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)

