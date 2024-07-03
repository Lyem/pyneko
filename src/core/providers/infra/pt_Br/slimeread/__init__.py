import json
from typing import List
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Chapter, Pages, Manga

class SlimeReadProvider(Base):
    name = 'Slime Read'
    icon = 'https://i.imgur.com/QRjE79s.png'
    icon_hash = 'd/iFDQIoqraAa360R1NPCZWlHiugekWiJw'
    lang = 'pt-Br'
    domain = 'slimeread.com'

    def __init__(self) -> None:
        self.base = 'https://slimeread.com'
        self.api = 'https://ola-scrapper-to-precisando-de-gente-bora.slimeread.com:8443'
        ua = UserAgent()
        user = ua.chrome
        self.headers = {'origin': 'slimeread.com','referer': f'{self.base}', 'User-Agent': user}
        self.cdn = 'https://black.slimeread.com/'
    
    def getMangas(self) -> List[Manga]:
        pass
    
    def getManga(self, link: str) -> Manga:
        id = link.split('/')[4]
        page = Http.get(f'{self.base}/manga/{id}', headers=self.headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        title = soup.select_one('p.text-3xl')
        return Manga(id, title.get_text())

    def _is_json(self, texto):
        try:
            json.loads(texto)
            return True
        except json.JSONDecodeError:
            return False

    def getChapters(self, id: str) -> List[Chapter]:
        list = []
        response = Http.get(f'{self.api}/book_cap_units_all?manga_id={id}', headers=self.headers)
        if(not self._is_json(response.content)):
            chs = BeautifulSoup(response.content, 'html.parser')
            pre_tag_content = chs.find('pre').text
            array = json.loads(pre_tag_content)
        else:
            array = response.json()
        page = Http.get(f'{self.base}/manga/{id}', headers=self.headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        title = soup.select_one('p.text-3xl')
        for chapter in array:
            list.append(Chapter(f'{id}/{chapter['btc_cap']}', int(chapter['btc_cap']) + 1, title.get_text()))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        list = []
        ids = ch.id.split('/')
        response = Http.get(f'{self.api}/book_cap_units?manga_id={ids[0]}&cap={ids[1]}', headers=self.headers)
        if(not self._is_json(response.content)):
            pages = BeautifulSoup(response.content, 'html.parser')
            pre_tag_content = pages.find('pre').text
            api_content = json.loads(pre_tag_content)
        else:
            api_content = response.json()
        for data in api_content[0]['book_temp_cap_unit']:
            if(data['btcu_image'] != 'folders/pagina_inicial.png' and data['btcu_image'] != 'folders/pagina_final.png'):
                list.append(f'{self.cdn}{data['btcu_image']}')
        return Pages(ch.id, ch.number, ch.name, list)

