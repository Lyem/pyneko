from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class SafireScanProvider(Base):
    name = 'Safire Scans'
    lang = 'pt_Br'
    domain = ['www.safirescan.xyz']

    def __init__(self) -> None:
        pass
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div h1.my-2.text-2xl')

        return Manga(link, title.get_text(strip=True))

    def getChapters(self, id: str) -> List[Chapter]:
        list = []
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div h1.my-2.text-2xl')
        subtitles = soup.select_one('div p')
        array_sub = subtitles.get_text().split(',')
        for subs in array_sub:
            response = Http.get(f'https://www.safirescan.xyz/feeds/posts/default/-/{subs.strip()}?alt=json&start-index=1&max-results=150').json()
            if 'feed' in response and 'entry' in response['feed']:
                for ch in response['feed']['entry']:
                    if ch['link'][-1]['href'] != id:
                        list.append(Chapter(ch['link'][-1]['href'], ch['link'][-1]['title'], title.get_text(strip=True)))
                break
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        get_pages = soup.select('article#reader img')
        list = []
        for pgs in get_pages:
            list.append(pgs.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)

