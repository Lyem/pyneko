from core.download.infra import DownloadRepository
from core.providers.domain.page_entity import Pages
from core.download.domain.dowload_entity import Chapter
from core.__seedwork.application.use_cases import UseCase


class DownloadUseCase(UseCase):
    def execute(self, pages: Pages, fn=None, headers=None, cookies=None, timeout=None) -> Chapter:
        return DownloadRepository().download(pages, fn, headers, cookies, timeout=timeout)
