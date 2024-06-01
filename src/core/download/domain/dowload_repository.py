from .dowload_entity import Chapter
from abc import ABC
from core.providers.domain.page_entity import Pages


class DownloadRepository(ABC):
    @classmethod
    def download(pages: Pages, fn=None, headers=None, cookies=None) -> Chapter:
        raise NotImplementedError()
