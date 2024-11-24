from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class VortexScansProvider(Base):
    name = 'Vortex Scans'
    lang = 'en'
    domain = ['vortexscans.org']

    def __init__(self) -> None:
        self.base = 'https://vortexscans.org/api'
        self.url = 'https://vortexscans.org'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1.text-2xl')

        return Manga(link, title.get_text().strip())

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1.text-2xl')
        search = Http.get(f'{self.base}/query?searchTerm={title.get_text().strip()}&perPage=4').json()
        response = Http.get(f'{self.base}/chapters?postId={search['posts'][0]['id']}&skip=0&take=99999&order=desc').json()
        list = []
        for ch in response['post']['chapters']:
            number = f'Chapter {ch['number']}'
            list.append(Chapter(f'{self.url}/series/{ch['mangaPost']['slug']}/{ch['slug']}', number, title.get_text().strip()))
        return list
    
    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        img_div = soup.select_one('section.w-full.flex.flex-col.justify-center.items-center')
        images = img_div.select('img')
        list = []
        for imgs in images:
            list.append(imgs.get('src'))
        return Pages(ch.id, ch.number, ch.name, list)

