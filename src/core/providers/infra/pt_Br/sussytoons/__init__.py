import re
from typing import List
from core.__seedwork.infra.http import Http
from urllib.parse import urlparse, parse_qs
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class NewSussyToonsProvider(Base):
    name = 'New Sussy Toons'
    lang = 'pt_Br'
    domain = ['new.sussytoons.site']

    def __init__(self) -> None:
        self.base = 'https://api.sussytoons.site'
        self.CDN = 'https://cdn.sussytoons.site'
    
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
        response = Http.get(f'{self.base}/obras/{id_value}/capitulos?limite=9999999999').json()
        list = []
        for ch in response['resultados']:
            list.append(Chapter(ch['cap_id'], ch['cap_nome'], title))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(f'{self.base}/capitulos/{ch.id}').json()
        list = []
        for pg in response['resultado']['cap_paginas']:
            if response['resultado']['cap_imagem'] == None:
                if "?t=" in pg['src'] and pg['src'].startswith("?t="):
                    continue
                page = f'{self.CDN}/storage/wp-content/uploads/WP-manga/data/{pg['src']}?cache=/scans/1/obras/{response['resultado']['obra']['obr_id']}/capitulos/{response['resultado']['cap_numero']}'
            else:
                if "?t=" in pg['src'] and pg['src'].startswith("?t="):
                    continue

                page = f'{self.CDN}/scans/1/obras/{response['resultado']['obra']['obr_id']}/capitulos/{response['resultado']['cap_numero']}/{pg['src']}'
            list.append(page)
        return Pages(ch.id, ch.number, ch.name, list)