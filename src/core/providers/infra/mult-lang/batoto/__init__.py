import re
import json
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class BatotoProvider(Base):
    name = 'Batoto'
    lang = 'mult'
    domain = ['wto.to', 'bato.to', 'battwo.com', 'batotoo.com', 'xbato.net', 'xbato.com']

    def __init__(self) -> None:
        self.base = 'https://wto.to'
        self.headers = {'referer': f'{self.base}'}
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h3.item-title > a')
        return Manga(link, title.get_text())

    def getChapters(self, link: str) -> List[Chapter]:
        list = []
        response = Http.get(link, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        chs = soup.select('a.visited.chapt')
        title = soup.select_one('h3.item-title > a')
        for chapter in chs:
            list.append(Chapter(f'{self.base}{chapter.get('href')}', chapter.select_one('b').get_text(), title.get_text()))
        list.reverse()
        return list

    def getPages(self, ch: Chapter) -> Pages:
        list = []
        response = Http.get(ch.id, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'const imgHttps =' in script.string:
                match = re.search(r'const imgHttps = (\[.*?\]);', script.string, re.DOTALL)
                if match:
                    img_https_value = match.group(1)
                    break
        if img_https_value:
            img_https_list = json.loads(img_https_value)
            list = img_https_list
        return Pages(ch.id, ch.number, ch.name, list)

