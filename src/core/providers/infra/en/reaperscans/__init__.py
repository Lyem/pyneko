from typing import List
from urllib.parse import urlparse, parse_qs
from core.__seedwork.infra.http import Http
from bs4 import BeautifulSoup
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class ReaperScansProvider(Base):
    name = 'Reaper Scans'
    lang = 'en'
    domain = ['reaperscans.com']

    def __init__(self) -> None:
        self.base = 'https://api.reaperscans.com'
        self.url = 'https://reaperscans.com'
    
    def getManga(self, link: str) -> Manga:
        path = urlparse(link).path
        slug = path.strip("/").split("/")[-1]
        response = Http.get(f'{self.base}/series/{slug}').json()
        title = response['title']

        return Manga(link, title)

    def getChapters(self, id: str) -> List[Chapter]:
        path = urlparse(id).path
        slug = path.strip("/").split("/")[-1]
        response = Http.get(f'{self.base}/series/{slug}').json()
        title = response['title']
        series_id = response['id']
        response = Http.get(f'{self.base}/chapter/query?page=1&perPage=9999999&query=&order=desc&series_id={series_id}').json()
        list = []
        for ch in response['data']:
            list.append(Chapter(f'{self.url}/series/{ch['series']['series_slug']}/{ch['chapter_slug']}', ch['chapter_name'], title))
        return list

    def link_formatter(self, encoded_url: str) -> str:
        query = urlparse(encoded_url).query
        params = parse_qs(query)
        url_value = params.get("url", [None])[0]

        return url_value
    
    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        get_pages = soup.select_one('div#content > div.container')
        get_page = get_pages.select('img')
        list = []
        for pg in get_page:
            src = pg.get('srcset')
            list.append(self.link_formatter(src))
        print(list)
        return Pages(ch.id, ch.number, ch.name, list)