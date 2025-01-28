import re
from typing import List
from bs4 import BeautifulSoup
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
        self.oldCDN = 'https://oldi.sussytoons.site/scans/1/obras'
        self.webBase = 'https://www.sussytoons.site'
    
    def getManga(self, link: str) -> Manga:
        match = re.search(r'/obra/(\d+)', link)
        id_value = match.group(1)
        response = Http.get(f'{self.base}/obras/{id_value}').json()
        title = response['resultado']['obr_nome']
        return Manga(link, title)

    def getChapters(self, id: str) -> List[Chapter]:
        try:
            match = re.search(r'/obra/(\d+)', id)
            id_value = match.group(1)
            response = Http.get(f'{self.base}/obras/{id_value}').json()
            title = response['resultado']['obr_nome']
            list = []
            for ch in response['resultado']['capitulos']:
                list.append(Chapter([id_value, ch['cap_id'], ], ch['cap_nome'], title))
            return list
        except Exception as e:
            print(e)

    def getPages(self, ch: Chapter) -> Pages:
            try:
                response = Http.get(f'{self.webBase}/capitulo/{ch.id[1]}')
                soup = BeautifulSoup(response.content, 'html.parser')
                get_images = soup.select('img.chakra-image.css-1hgt80r')
                list = []
                for images in get_images:
                    list.append(images.get('src'))

                return Pages(ch.id, ch.number, ch.name, list)
            
            except Exception as e:
                print(e)
