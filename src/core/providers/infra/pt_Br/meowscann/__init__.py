from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class MeowScannProvider(Base):
    name = 'Meow Scann'
    lang = 'pt_Br'
    domain = ['meowscan1.blogspot.com']

    def __init__(self) -> None:
        self.API_domain = 'meowscan1.blogspot.com'
        self.cookie = {'INTERSTITIAL': 'ABqL8_j9iNX3aHhf2VR_tVo_UBu0PZk5TTu29be9X72JDH_DQweTZ4YGL2mMmPk'}
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link, cookies=self.cookie)
        soup = BeautifulSoup(response.content)
        title = soup.select_one('article strong')
        
        return Manga(link, title.get_text(strip=True))
    
    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id, cookies=self.cookie)
        soup = BeautifulSoup(response.content)
        title = soup.select_one('article strong')
        response = Http.get(f'https://{self.API_domain}/feeds/posts/default/-/{title.get_text(strip=True)}?alt=json&start-index=1&max-results=150').json()
        list = []
        for ch in response['feed']['entry']:
            if ch['link'][4]['title'] == title.get_text(strip=True):
                continue
            list.append(Chapter(ch['link'][4]['href'], ch['title']['$t'], title.get_text(strip=True)))
        return list
    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        get_images = soup.select('div.separator a img')
        list = []
        for img in get_images:
            list.append(img.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)

