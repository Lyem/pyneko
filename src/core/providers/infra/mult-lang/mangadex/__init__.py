from typing import List
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class MangaDexProvider(Base):
    name = 'MangaDex'
    lang = 'mult-lang'
    domain = ['mangadex.org']

    def __init__(self) -> None:
        self.Api = 'https://api.mangadex.org'
        self.CDN = 'https://cmdxd98sb0x3yprd.mangadex.network/data'
    
    def getManga(self, link: str) -> Manga:
        get_uuid = link.split('/')
        response = Http.get(f'{self.Api}/manga/{get_uuid[4]}?includes[]=manga').json()
        title = response['data']['attributes']['title']['en']
        return Manga(link, title)
    
    def getChapters(self, id: str) -> List[Chapter]:
        get_uuid = id.split('/')
        response = Http.get(f'{self.Api}/manga/{get_uuid[4]}?includes[]=manga').json()
        title = response['data']['attributes']['title']['en']
        response = Http.get(f'{self.Api}/manga/{get_uuid[4]}/feed?translatedLanguage[]=pt-br&limit=100&order[volume]=desc&order[chapter]=desc&offset=0&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic').json()
        list = []
        for ch in response['data']:
            list.append(Chapter(ch['id'], f'Capítulo {ch['attributes']['chapter']}', title))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        try:
            response = Http.get(f'{self.Api}/at-home/server/{ch.id}?forcePort443=false').json()
            hash_code = response['chapter']['hash']
            list = []
            for pgs in response['chapter']['data']:
                list.append(f'{self.CDN}/{hash_code}/{pgs}')
            return Pages(ch.id, ch.number, ch.name, list)
        except Exception as e:
            print(e)

