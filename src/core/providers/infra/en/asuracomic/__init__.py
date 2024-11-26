import re
import json
from typing import List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class AsuraComicProvider(Base):
    name = 'Asura Scans'
    lang = 'en'
    domain = ['asuracomic.net']

    def __init__(self) -> None:
        self.url = 'https://asuracomic.net/series/'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('span.text-xl.font-bold')
        return Manga(link, title.get_text().strip())

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('span.text-xl.font-bold')
        chapters = soup.select('h3 > a.flex.flex-row ')
        list = []
        for ch in chapters:
            list.append(Chapter(f'{self.url}{ch.get('href')}', ch.get_text().strip(), title.get_text().strip()))
        list.reverse()
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.select('script')
        pattern = re.compile(r'\\"order\\":\s*(\d+),\s*\\"url\\":\s*\\"(https?://[^"]+)\\"')

        result = {}

        for script in scripts:
            if script.string and "self.__next_f.push" in script.string:
                matches = pattern.findall(script.string)
                for match in matches:
                    order, url = match
                    if url not in result:
                        result[url] = int(order)

        sorted_urls = [url for url, _ in sorted(result.items(), key=lambda x: x[1])]

        return Pages(ch.id, ch.number, ch.name, sorted_urls)
