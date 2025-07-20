import re
from typing import List
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class YugenProvider(Base):
    name = 'Yugen mangas'
    lang = 'pt-Br'
    domain = [re.compile(r'\byugenmangasbr\.[^\s/]+(?:\.[^\s/]+)*\b')]

    def __init__(self) -> None:
        self.base = 'https://yugenmangasbr.yocat.xyz/'
        self.cdn = 'https://media.yugenweb.com/'
        self.api = 'https://api.yugenweb.com/'
        self.headers = {'referer': f'{self.base}'}

    def getManga(self, link: str) -> Manga:
        if link.endswith('/'):
            link = link[:-1]
        id = link.split("/").pop();
        response = Http.post(f'{self.api}api/series/detail/series/', json={'code': id})
        data = response.json()
        return Manga(id, data['title'])
    
    def getChapters(self, id: str) -> List[Chapter]:
        media_response = Http.post(f'{self.api}api/series/detail/series/', json={'code': id})
        media_data = media_response.json()
        response = Http.post(f'{self.api}api/series/chapters/get-series-chapters/?page=1', json={
            "code": id,
            "reverse": False
        })
        data = response.json()
        list = []
        for ch in data['results']['chapters']:
            list.append(Chapter(ch['code'], ch['name'], media_data['title']))
        while data['next'] != None:
            response = Http.post(f'{data['next']}', json={
                "code": id,
                "reverse": False
            })
            data = response.json()
            for ch in data['results']['chapters']:
                list.append(Chapter(ch['code'], ch['name'], media_data['title']))

        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.post(f'{self.api}api/chapters/chapter-info/', json={
            "code": ch.id,
            "key":"mOlh8W0u5LnoaaYbuJdBYgrDjidseyyn",
        })
        data = response.json()

        links = []

        for link in data['images']:
            links.append(f'{self.cdn}{link}')

        return Pages(ch.id, ch.number, ch.name, links)
