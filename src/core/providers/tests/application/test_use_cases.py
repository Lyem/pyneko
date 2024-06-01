from core.providers.infra.pt_Br.tsuki import TsukiProvider
from core.providers.application.use_cases import ProviderMangasUseCase
from core.providers.domain.entities import Manga

class TestUseCaseProvider:
    def test_mangas(self):
        response = ProviderMangasUseCase(TsukiProvider).execute()
        assert len(response) > 0
        for manga in response:
            assert isinstance(manga, Manga)
