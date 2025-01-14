import re
from typing import List
from core.__seedwork.infra.http import Http
from urllib.parse import urlparse, parse_qs
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class NewSussyToonsProvider(Base):
    name = 'New Sussy Toons'
    lang = 'pt_Br'
    domain = ['new.sussytoons.site', 'www.sussyscan.com', 'www.sussytoons.site']

    def __init__(self) -> None:
        self.base = 'https://api-dev.sussytoons.site'
        self.CDN = 'https://cdn.sussytoons.site'
        self.old = 'https://oldi.sussytoons.site/wp-content/uploads/WP-manga/data/'
    
    def getManga(self, link: str) -> Manga:
        match = re.search(r'/obra/(\d+)', link)
        id_value = match.group(1)
        response = Http.get(f'{self.base}/obras/{id_value}').json()
        title = response['resultado']['obr_nome']
        return Manga(link, title)

    def getChapters(self, id: str) -> List[Chapter]:
        match = re.search(r'/obra/(\d+)', id)
        id_value = match.group(1)
        response = Http.get(f'{self.base}/obras/{id_value}').json()
        title = response['resultado']['obr_nome']
        list = []
        for ch in response['resultado']['capitulos']:
            list.append(Chapter(ch['cap_id'], ch['cap_nome'], title))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(f'{self.base}/capitulos/{ch.id}').json()
        try:
            response = Http.get(f'{self.base}/{response["obra"]["scan_id"]}/capitulos/{ch.id}', headers={'scan-id': '1'}).json()
        except Exception as e:
            print(e)
        try:
            list = []
            for pg in response['resultado']['cap_paginas']:
                page = f'{self.old}{pg['src']}'
                list.append(page)
            return Pages(ch.id, ch.number, ch.name, list)
        except Exception as e:
            print(e)