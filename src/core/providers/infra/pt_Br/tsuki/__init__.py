import os
from typing import List
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Chapter, Pages, Manga

class TsukiProvider(Base):
    name = 'Tsuki Mangas'
    lang = 'pt-Br'
    domain = 'tsuki-mangas.com'

    def __init__(self) -> None:
        self.base = 'https://tsuki-mangas.com'
        self.headers = {'referer': f'{self.base}'}
        self.cdns = ['https://cdn.tsuki-mangas.com/tsuki', 'https://cdn1.tsuki-mangas.com/imgs', 'https://cdn2.tsuki-mangas.com']
    
    def getManga(self, link: str) -> Manga:
        id = link.split('/')[4]
        response = Http.get(f'{self.base}/api/v3/mangas/{id}', headers=self.headers).json()
        return Manga(response['id'], response['title'])

    def getChapters(self, id: str) -> List[Chapter]:
        list = []
        manga = Http.get(f'{self.base}/api/v3/mangas/{id}', headers=self.headers).json()
        response = Http.get(f'{self.base}/api/v3/chapters/{id}/all', headers=self.headers).json()
        for chapter in response['chapters']:
            list.append(Chapter(chapter['versions'][0]['id'], chapter['number'], str(manga['title'])))
        return list

    def _extract_number_from_page_url(self, url):
        return os.path.basename(url.split("?")[0])

    def getPages(self, ch: Chapter) -> Pages:
        list = []
        response = Http.get(f'{self.base}/api/v3/chapter/versions/{ch.id}', headers=self.headers).json()
        cdn_selected = ''
        for data in response['pages']:
            if len(cdn_selected) == 0:
                for cdn in self.cdns:
                    r = Http.get(f'{cdn}{data['url']}', headers=self.headers)
                    if r.status == 200:
                        cdn_selected = cdn
                        break
            list.append(f'{cdn_selected}{data['url']}')

        return Pages(id, ch.number, response['chapter']['manga']['title'], sorted(list, key=self._extract_number_from_page_url))
  
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        if headers is not None:
            headers = headers | self.headers
        else:
            headers = self.headers
        DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)

