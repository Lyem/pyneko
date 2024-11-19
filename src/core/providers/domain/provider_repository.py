from typing import List
from abc import ABC, abstractmethod
from .entities import Chapter, Pages, Manga

class ProviderRepository(ABC):
    name: str
    lang: str
    domain: str
    has_login: bool = False

    @abstractmethod
    def login() -> None:
        raise NotImplementedError()
    
    @abstractmethod
    def getManga(link: str) -> Manga:
        raise NotImplementedError()

    @abstractmethod
    def getChapters(id: str) -> List[Chapter]:
        raise NotImplementedError()
    
    @abstractmethod
    def getPages(ch: Chapter) -> Pages:
        raise NotImplementedError()
    
    @abstractmethod
    def download(pages: Pages, fn: any):
        raise NotImplementedError()
