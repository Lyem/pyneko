import re
from typing import List
from bs4 import BeautifulSoup
from tldextract import extract
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Chapter, Pages, Manga

class NewTokiProvider(Base):
    name = 'New Toki'
    lang = 'ko'
    domain = [re.compile(r'^newtoki\d*\.com$')]
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div.col-sm-8')
        title = title.select_one('div.view-content')
        title = title.select_one('span')
        title = title.select_one('b').get_text().strip()
        return Manga(link, title)

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div.col-sm-8')
        title = title.select_one('div.view-content')
        title = title.select_one('span')
        title = title.select_one('b').get_text().strip()
        list_body = soup.select_one('ul.list-body')
        caps = list_body.select('li')
        list = []
        for cap in caps:
            a = cap.select_one('div.wr-subject')
            a = a.select_one('a.item-subject')
            for span in a.find_all('span'):
                span.extract()
            list.append(Chapter(a.get('href'), a.get_text().strip(), title))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        print(f'[no-render] {response.content}')
        soup = BeautifulSoup(response.content, 'html.parser')
        imgs = soup.select('p > img')
        list = []
        for img in imgs:
            src = img.get('src')
            if src != "":
                list.append(src)
        return Pages(ch.id, ch.number, ch.name, list)

    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        extract_info = extract(pages.id)
        domain = f"{extract_info.domain}.{extract_info.suffix}"
        headers = {'referer': f'https://{domain}'}
        return DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)

