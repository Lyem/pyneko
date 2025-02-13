import re
import nodriver as uc
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Chapter, Pages
from core.providers.infra.template.manga_reader_cms import MangaReaderCms

class DiskusScanProvider(MangaReaderCms):
    name = 'Diskus Scan'
    lang = 'pt-Br'
    domain = ['diskusscan.online']

    def __init__(self):
        super().__init__()
        self.url = 'https://diskusscan.online'
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'div#chapterlist ul li'
        self.query_pages = 'img.attachment-full.size-full'
        self.query_title_for_uri = 'h1.entry-title'

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
    
    # def getPageContent(self, domain: str, background = False) -> any:
    #     content= ''
    #     async def get_script_result():
    #         nonlocal content
    #         browser = await uc.start(
    #             browser_args=[
    #                 '--window-size=600,600', 
    #                 f'--app={domain}',
    #                 '--disable-extensions', 
    #                 '--disable-popup-blocking'
    #             ],
    #             browser_executable_path=None,
    #             headless=background
    #         )
    #         page = await browser.get(domain)
    #         data = []
    #         while len(data) == 0:
    #             page_content = await page.evaluate('document.documentElement.outerHTML')
    #             soup = BeautifulSoup(page_content, 'html.parser')
    #             data = soup.select(self.query_chapters)

    #         content = page_content
    #         browser.stop()
    #     uc.loop().run_until_complete(get_script_result())
    #     return content
    
    # def getChapters(self, id: str) -> List[Chapter]:
    #     response = self.getPageContent(urljoin(self.url, id), True)
    #     soup = BeautifulSoup(response, 'html.parser')
    #     data = soup.select(self.query_chapters)
    #     title = soup.select(self.query_title_for_uri)[0].text.strip()
    #     chapters = []
    #     for element in data:
    #         anchor = element if element.name == 'a' else element.select_one('a')
    #         chapters.append(Chapter(
    #             id=self.get_relative_link(anchor),
    #             number=element.select('span.chapternum')[0].text,
    #             name=title
    #         ))
    #     chapters.reverse()
    #     return chapters
    