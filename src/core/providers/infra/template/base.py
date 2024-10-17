from typing import List
from core.providers.domain.provider_repository import ProviderRepository
from core.providers.domain.entities import Chapter, Pages, Manga
from core.download.application.use_cases import DownloadUseCase

class Base(ProviderRepository):
    name = ''
    lang = ''
    domain = ''

    def getManga(link: str) -> Manga:
        raise NotImplementedError()

    def getChapters(id: str) -> List[Chapter]:
        raise NotImplementedError()
    
    def getPages(ch: Chapter) -> Pages:
        raise NotImplementedError()
    
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)
