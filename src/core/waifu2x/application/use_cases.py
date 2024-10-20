from core.waifu2x.infra import UpscaleRepository
from core.download.domain.dowload_entity import Chapter
from core.__seedwork.application.use_cases import UseCase


class Waifu2xUseCase(UseCase):
    def execute(self, ch: Chapter, fn=None) -> Chapter:
        return UpscaleRepository().upscale(ch, fn)
