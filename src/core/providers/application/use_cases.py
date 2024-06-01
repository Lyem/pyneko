from typing import List
from core.__seedwork.application.use_cases import UseCase
from core.providers.domain.entities import Chapter, Pages, Manga
from core.providers.domain.provider_repository import ProviderRepository
from tinydb import TinyDB, where
from core.config.mangas_cache import MangasCache
from platformdirs import user_cache_path
from os import makedirs

cache_path = user_cache_path('pyneko')
db_path = cache_path / 'mangas.json'
makedirs(cache_path, exist_ok=True)
db = TinyDB(db_path)

class ProviderMangaUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self, link: str) -> Manga:
        return self.provider().getManga(link)

class ProviderMangasUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self) -> List[Manga]:
        mangas_cache = db.search(where('domain') == self.provider.domain)
        if(len(mangas_cache) > 0):
            mangas = MangasCache.from_dict(mangas_cache[0]).mangas
        else:
            mangas = self.provider().getMangas()
            db.insert(MangasCache(domain=self.provider.domain, mangas=mangas).as_dict())
        return mangas

class ProviderCleanMangasCacheUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self) -> None:
        mangas_cache = db.search(where('domain') == self.provider.domain)
        if(len(mangas_cache) > 0):
            mangas_cache.remove()


class ProviderGetChaptersUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self, id: str) -> List[Chapter]:
        return self.provider().getChapters(id)


class ProviderGetPagesUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self, id: str) -> Pages:
        return self.provider().getPages(id)

class ProviderDownloadUseCase(UseCase):
    def __init__(self, provider: ProviderRepository) -> None:
        self.provider = provider

    def execute(self, pages: Pages, fn: any) -> None:
        return self.provider().download(pages=pages, fn=fn)
