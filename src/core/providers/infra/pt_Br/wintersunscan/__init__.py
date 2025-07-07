from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class WinterSunScanProvider(Base):
    name = 'Winter Sun Scan'
    lang = 'pt_Br'
    domain = ['wintersunscan.com']

    def __init__(self) -> None:
        pass
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title =  soup.select_one('head meta[property="og:title"]')
        return Manga(link, title)


    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title =  soup.select_one('head meta[property="og:title"]')
        get_chapters_div = soup.select_one('div.specmobile.row')
        list = []
        for ch in get_chapters_div:
            onclick = ch.select_one('div.card-caps.d-flex.align-items-center')
            url = onclick.get('onclick').split("'")[1]
            list.append(Chapter(url, ch.select_one('span.color-white.d-block'), title))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.select('div.d-flex.justify-content-center.align-items-center.flex-column img')
        list = []
        for img in images:
            list.append(img.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)

