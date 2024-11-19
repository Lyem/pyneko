from typing import List
from core.__seedwork.application.use_cases import UseCase
from core.providers.domain.entities import Chapter, Pages, Manga
from core.download.domain.dowload_entity import Chapter as ChapterDw
from core.providers.domain.provider_repository import ProviderRepository

class ProviderLoginUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self) -> None:
        return self.provider().login()

class ProviderMangaUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self, link: str) -> Manga:
        return self.provider().getManga(link)

class ProviderGetChaptersUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self, id: str) -> List[Chapter]:
        return self.provider().getChapters(id)


class ProviderGetPagesUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self, ch: Chapter) -> Pages:
        return self.provider().getPages(ch)

class ProviderDownloadUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self, pages: Pages, fn: any) -> ChapterDw:
        return self.provider().download(pages=pages, fn=fn)
