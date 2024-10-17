import re
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

class NineMangasProvider(Base):
    name = 'Nine Mangas'
    icon = 'https://i.imgur.com/ycuyRsy.png'
    icon_hash = 'T3mBA4AkUz9sptRplgCb9VU7iHiQiYc'
    lang = 'pt_Br'
    domain = 'br.ninemanga.com'

    def __init(self) -> None:
        self.base = 'https://br.ninemanga.com'
        
    def getMangas(self) -> List[Manga]:
        pass
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        info = soup.select_one('ul.message')
        title = info.select_one('span')

        return Manga(link, title.get_text().strip())
    
    def add_query_param_if_missing(self, url, param, value):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if param not in query_params:
            query_params[param] = value
        new_query_string = urlencode(query_params, doseq=True)
        new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, 
                            parsed_url.params, new_query_string, parsed_url.fragment))
        return new_url
    
    def ten_pages_url(self, url):
        if url.endswith('.html'):
            url_modify = url.replace('.html', '-10-1.html')
            return url_modify
        else:
            return url
    
    def extract_numbers(self, text):
        padrao = r"(\d+(?:\.\d+)?)$"
        match = re.search(padrao, text)
        
        if match:
            return match.group(0)
        else:
            return text
    
    def getChapters(self, id: str) -> List[Chapter]:
        url = self.add_query_param_if_missing(id, 'waring', '1')
        response = Http.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        info = soup.select_one('ul.message')
        title = info.select_one('span')
        chapter_div = soup.select_one('div.silde')
        chapters = chapter_div.select('a.chapter_list_a')
        list = []
        for chapter in chapters:
            list.append(Chapter(self.ten_pages_url(chapter.get('href')), self.extract_numbers(chapter.get('title')), title.get_text().strip()))
        return list


    def getPages(self, ch: Chapter) -> Pages:
        list = []
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        div_pages = soup.select_one('div.changepage')
        urls = div_pages.select('option')[1:]
        page_div = soup.select('center')[1]
        pages = page_div.select('img.manga_pic')
        for pg in pages:
            list.append(pg.get('src'))
        for url in urls:
            response = Http.get(f'{self.base}{url.get('value')}')
            soup = BeautifulSoup(response.content, 'html.parser')
            page_div = soup.select('center')[1]
            pages = page_div.select('img.manga_pic')
            for pg in pages:
                list.append(pg.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)