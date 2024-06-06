from typing import List
import json
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class YugenProvider(Base):
    name = 'Yugen mangas'
    icon = 'https://i.imgur.com/QRjE79s.png'
    icon_hash = 'd/iFDQIoqraAa360R1NPCZWlHiugekWiJw'
    lang = 'pt-Br'
    domain = 'yugenmangas.net.br'

    def __init__(self) -> None:
        self.base = 'https://yugenmangas.net.br'
        self.cdn = 'https://api.yugenmangas.net.br/'
        self.headers = {'referer': f'{self.base}'}
    
    def getMangas(self) -> List[Manga]:
        response = Http.get(f'{self.base}/series')
        soup = BeautifulSoup(response.content, 'html.parser')

        script_tag = soup.find('script', {'id': '__NUXT_DATA__'})

        script_content = script_tag.contents[0]

        script_content = script_content.strip()

        data = json.loads(script_content)
        names_and_slugs = [(item["name"], item["slug"]) for item in data if isinstance(item, dict) and "name" in item and "slug" in item]

        list = []
        for name, slug in names_and_slugs:
            list.append(Manga(data[slug].replace('series/', ''), data[name]))
        return list

    def getManga(self, link: str) -> Manga:
        slug = link.split("/")[-1]
        response = Http.post(f'{self.cdn}api/serie/serie_details/{slug}')
        data = response.json()
        return Manga(data['slug'], data['name'])

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.post(f'{self.cdn}api/chapters/get_chapters_by_serie/', json={
            "serie_slug": id
        })
        data = response.json()
        list = []
        for ch in data['chapters']:
            list.append(Chapter(f'{id}/{ch['slug']}', ch['name'], id.replace('-', ' ')))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(f'{self.base}/series/{ch.id}')

        soup = BeautifulSoup(response.content, 'html.parser')

        script_tag = soup.find('script', {'id': '__NUXT_DATA__'})

        script_content = script_tag.contents[0]

        script_content = script_content.strip()

        data = json.loads(script_content)

        imgs = data[4]
        
        links = []
        for img in imgs:
            links.append(f'{self.cdn}{data[img]}')
        return Pages(ch.id, ch.number, ch.name, links)