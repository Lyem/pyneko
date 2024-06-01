from typing import List
from abc import ABC, abstractmethod
from .entities import Chapter, Pages, Manga

class ProviderRepository(ABC):
    name: str
    icon: str
    icon_hash: str
    lang: str
    domain: str

    @abstractmethod
    def getMangas() -> List[Manga]:
        raise NotImplementedError()
    
    @abstractmethod
    def getManga(link: str) -> Manga:
        raise NotImplementedError()

    @abstractmethod
    def getChapters(id: str) -> List[Chapter]:
        raise NotImplementedError()
    
    @abstractmethod
    def getPages(id: str) -> Pages:
        raise NotImplementedError()
    
    @abstractmethod
    def download(pages: Pages, fn: any):
        raise NotImplementedError()
