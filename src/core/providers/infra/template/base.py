from typing import List
from core.providers.domain.provider_repository import ProviderRepository
from core.providers.domain.entities import Chapter, Pages, Manga
from core.download.application.use_cases import DownloadUseCase

class Base(ProviderRepository):
    name = ''
    icon = 'https://i.imgur.com/EvOBEp6.png'
    icon_hash = 'AAiCBQAjpQ1HiXl0aQt+p9kgJ0iFeYDKVw'
    lang = ''
    domain = ''

    def getMangas() -> List[Manga]:
        raise NotImplementedError()
    
    def getManga(link: str) -> Manga:
        raise NotImplementedError()

    def getChapters(id: str) -> List[Chapter]:
        raise NotImplementedError()
    
    def getPages(id: str) -> Pages:
        raise NotImplementedError()
    
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)
