from typing import List
from fake_useragent import UserAgent
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Chapter, Pages, Manga

class TsukiProvider(Base):
    name = 'Tsuki Mangas'
    icon = 'https://i.imgur.com/QRjE79s.png'
    icon_hash = 'd/iFDQIoqraAa360R1NPCZWlHiugekWiJw'
    lang = 'pt-Br'
    domain = 'tsuki-mangas.com'

    def __init__(self) -> None:
        self.base = 'https://tsuki-mangas.com'
        ua = UserAgent()
        user = ua.random
        self.headers = {'referer': f'{self.base}'}
    
    def getMangas(self) -> List[Manga]:
        list = []
        response = Http.get(f'{self.base}/api/v3/mangas?page=1', headers=self.headers).json()
        last_page = response['lastPage']
        for page in range(1, last_page):
            response = Http.get(f'{self.base}/api/v3/mangas?page={page}', headers=self.headers).json()
            for manga in response['data']:
                list.append(Manga(manga['id'], manga['title']))

        return list
    
    def getManga(self, link: str) -> Manga:
        id = link.split('/')[4]
        response = Http.get(f'{self.base}/api/v3/mangas/{id}', headers=self.headers).json()
        return Manga(response['id'], response['title'])

    def getChapters(self, id: str) -> List[Chapter]:
        list = []
        response = Http.get(f'{self.base}/api/v3/chapters/{id}/all', headers=self.headers).json()
        for chapter in response['chapters']:
            list.append(Chapter(chapter['versions'][0]['id'], chapter['number'], str(chapter['title'])))
        return list

    def getPages(self, id: str) -> Pages:
        list = []
        response = Http.get(f'{self.base}/api/v3/chapter/versions/{id}', headers=self.headers).json()
        for data in response['pages']:
            if(data['server'] == 1):
                list.append(f'https://cdn.tsuki-mangas.com/tsuki{data['url']}')
            else:
                list.append(f'https://cdn1.tsuki-mangas.com/imgs/{data['url']}')
        return Pages(id, str(response['chapter']['number']), str(response['chapter']['manga']['title']), list)
  
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        if headers is not None:
            headers = headers | self.headers
        else:
            headers = self.headers
        DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)

    

