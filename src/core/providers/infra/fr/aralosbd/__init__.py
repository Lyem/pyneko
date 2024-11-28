import json
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from urllib.parse import urlparse, parse_qs
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class AralosBDProvider(Base):
    name = 'AralosBD'
    lang = 'fr'
    domain = ['aralosbd.fr']

    def __init__(self) -> None:
        self.base = 'https://aralosbd.fr'
    
    def getManga(self, link: str) -> Manga:
        parsed_url = urlparse(link)
        query_params = parse_qs(parsed_url.query)
        id_value = query_params.get("id", [None])[0]
        response = Http.get(f'{self.base}/manga/api?get=manga&id={id_value}')
        chapters_data = json.loads(response.content)
        title = chapters_data['main_title']

        return Manga(link, title)

    def getChapters(self, id: str) -> List[Chapter]:
        parsed_url = urlparse(id)
        query_params = parse_qs(parsed_url.query)
        id_value = query_params.get("id", [None])[0]
        response = Http.get(f'{self.base}/manga/api?get=manga&id={id_value}')
        chapters_data = json.loads(response.content)
        title = chapters_data['main_title']
        response = Http.get(f'{self.base}/manga/api?get=chapters&manga={id_value}')
        chapters_data = json.loads(response.content)
        list = []
        for ch in chapters_data:
            list.append(Chapter(f'{self.base}/manga/api?get=pages&chapter={ch['chapter_id']}', f'Chapitre {ch['chapter_number']}', title))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        pages_data = json.loads(response.content)
        list = []
        for pg in pages_data['links']:
            list.append(f'{self.base}/{pg}')
        return Pages(ch.id, ch.number, ch.name, list)



