from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Chapter, Pages, Manga

class GreentoonProvider(Base):
    name = 'GreenToon'
    lang = 'ko'
    domain = ['greentoon.net']

    def __init__(self) -> None:
        self.base = 'https://greentoon.net'
        self.headers = {'referer': f'{self.base}'}
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div.info > h2')
        return Manga(link, title.get_text().strip())

    def getChapters(self, link: str) -> List[Chapter]:
        list = []
        response = Http.get(link, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        chapter_table = soup.select_one('#ep_list > ul')
        chs = chapter_table.select('a')
        title = soup.select_one('div.info > h2')
        for chapter in chs:
            list.append(Chapter(chapter.get('href'), chapter.select_one('div.subj').get_text(), title.get_text().strip()))
        list.reverse()
        return list

    def getPages(self, ch: Chapter) -> Pages:
        list = []
        response = Http.get(ch.id, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        pagesDiv = soup.select_one('div.toon_content')
        imgs = pagesDiv.select('img')
        for page in imgs:
            list.append(page.get('src'))
       
        return Pages(ch.id, ch.number, ch.name, list)

    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        if headers is not None:
            headers = headers | self.headers
        else:
            headers = self.headers
        return  DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)
