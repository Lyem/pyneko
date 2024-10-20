import nodriver as uc
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from core.providers.domain.entities import Chapter
from core.providers.infra.template.manga_reader_cms import MangaReaderCms

class GuildaTierDrawProvider(MangaReaderCms):
    name = 'Guilda Tier draw'
    lang = 'pt-Br'
    domain = ['www.guildatierdraw.top']

    def __init__(self):
        super().__init__()
        self.url = 'https://www.guildatierdraw.top'
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'div#clwd ul li'
        self.query_pages = 'div.check-box img'
        self.query_title_for_uri = 'h1.mt-0'
    
    def getPageContent(self, domain: str, background = False) -> any:
        content= ''
        async def get_script_result():
            nonlocal content
            browser = await uc.start(
                browser_args=[
                    '--window-size=600,600', 
                    f'--app={domain}',
                    '--disable-extensions', 
                    '--disable-popup-blocking'
                ],
                browser_executable_path=None,
                headless=background
            )
            page = await browser.get(domain)
            data = []
            while len(data) == 0:
                page_content = await page.evaluate('document.documentElement.outerHTML')
                soup = BeautifulSoup(page_content, 'html.parser')
                data = soup.select(self.query_chapters)

            content = page_content
            browser.stop()
        uc.loop().run_until_complete(get_script_result())
        return content
    
    def getChapters(self, id: str) -> List[Chapter]:
        response = self.getPageContent(urljoin(self.url, id), True)
        soup = BeautifulSoup(response, 'html.parser')
        data = soup.select(self.query_chapters)
        title = soup.select(self.query_title_for_uri)[0].text.strip()
        chapters = []
        for element in data:
            anchor = element if element.name == 'a' else element.select_one('a')
            chapters.append(Chapter(
                id=self.get_relative_link(anchor),
                number=element.select('span.chapternum')[0].text,
                name=title
            ))
        chapters.reverse()
        return chapters
    