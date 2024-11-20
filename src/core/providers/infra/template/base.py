from typing import List
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Chapter, Pages, Manga
from core.providers.domain.provider_repository import ProviderRepository

class Base(ProviderRepository):
    name = ''
    lang = ''
    domain = ['']
    has_login = False

    def login() -> None:
        raise NotImplementedError()

    def getManga(link: str) -> Manga:
        raise NotImplementedError()

    def getChapters(id: str) -> List[Chapter]:
        raise NotImplementedError()
    
    def getPages(ch: Chapter) -> Pages:
        raise NotImplementedError()
    
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        return DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)
