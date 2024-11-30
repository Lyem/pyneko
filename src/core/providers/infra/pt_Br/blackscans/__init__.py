from typing import List
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class BlackScansProvider(Base):
    name = 'Black Scans'
    lang = 'pt_Br'
    domain = ['blackscans.site']

    def __init__(self) -> None:
        self.base = 'https://api.blackscans.site/api'
        self.CDN = 'https://api.blackscans.site/media/'
    
    def getManga(self, link: str) -> Manga:
        id_obra = link.split("/")[-1]
        data = {"series_code": id_obra}
        response = Http.post(f'{self.base}/series/chapters/', json=data).json()

        return Manga(link, response['series_title'])

    def getChapters(self, id: str) -> List[Chapter]:
        id_obra = id.split("/")[-1]
        data = {"series_code": id_obra}
        response = Http.post(f'{self.base}/series/chapters/', json=data).json()
        list = []
        for ch in response['chapters']:
            list.append(Chapter(ch['code'], ch['name'], response['series_title']))
        return list
    
    def getPages(self, ch: Chapter) -> Pages:
        data = {"chapter_code": ch.id}
        response = Http.post(f'{self.base}/chapter/info/', json=data).json()
        list = []
        for pgs in response['images']:
            list.append(f'{self.CDN}{pgs}')
        return Pages(ch.id, ch.number, ch.name, list)

