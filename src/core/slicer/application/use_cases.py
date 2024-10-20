from core.slicer.infra import Slicer
from core.download.domain.dowload_entity import Chapter
from core.__seedwork.application.use_cases import UseCase


class SlicerUseCase(UseCase):
    def execute(self, ch: Chapter, fn=None) -> Chapter:
        return Slicer().run(ch, fn)
