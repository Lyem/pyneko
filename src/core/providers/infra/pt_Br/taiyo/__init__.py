import json
from typing import List
from urllib.parse import urlparse
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class TaiyoProvider(Base):
    name = 'Taiyo'
    lang = 'pt_Br'
    domain = ['taiyo.moe']

    def __init__(self) -> None:
        self.api = "https://taiyo.moe"
        self.cdn = "https://cdn.taiyo.moe/medias/"
    
    def getManga(self, link: str) -> Manga:
        parsed_url = urlparse(link)
        manga_id = parsed_url.path.split('/')[-1]
        
        response = Http.get(f'{self.api}/api/trpc/medias.getById?batch=1&input={json.dumps({"0": {"json": manga_id}})}')
        response_json = response.json()
        return Manga(manga_id, response_json[0]['result']['data']['json']['mainTitle'])

    def getChapters(self, manga_id: str) -> List[Chapter]:
        response = Http.get(f'{self.api}/api/trpc/medias.getById?batch=1&input={json.dumps({"0": {"json": manga_id}})}')
        response_json = response.json()
        title = response_json[0]['result']['data']['json']['mainTitle']
        
        response = Http.get(f'{self.api}/api/trpc/chapters.getByMediaId?batch=1&input={json.dumps({"0": {"json": {"mediaId": manga_id, "page": 1, "perPage": 30}}})}')
        response_json = response.json()
        
        chapters_list = []
        total_pages = response_json[0]['result']['data']['json']['totalPages']
        
        for index in range(total_pages):
            if index != 0:
                response = Http.get(f'{self.api}/api/trpc/chapters.getByMediaId?batch=1&input={json.dumps({"0": {"json": {"mediaId": manga_id, "page": index + 1, "perPage": 30}}})}')
                response_json = response.json()
            
            for chapter in response_json[0]['result']['data']['json']['chapters']:
                chapters_list.append(Chapter(chapter['id'], chapter['number'], title))
        
        return chapters_list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(f'{self.api}/api/trpc/chapters.getById?batch=1&input={json.dumps({"0": {"json": ch.id}})}')
        response_json = response.json()

        pages_list = []
        for page in response_json[0]['result']['data']['json']['pages']:
            pages_list.append(f"{self.cdn}{response_json[0]['result']['data']['json']['media']['id']}/chapters/{response_json[0]['result']['data']['json']['id']}/{page['id']}.{page['extension']}")
        
        return Pages(ch.id, f'{ch.number}', ch.name, pages_list)

