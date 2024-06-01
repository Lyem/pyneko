from core.providers.infra.pt_Br.tsuki import TsukiProvider
from core.providers.domain.entities import Chapter, Pages, Manga

class TestTsukiProvider:
    def test_mangas(self):
        response = TsukiProvider().getMangas()
        assert len(response) > 0
        for manga in response:
            assert isinstance(manga, Manga)

    def test_manga(self):
        response = TsukiProvider().getManga('https://tsuki-mangas.com/obra/9987/the-demon-king-who-lost-his-job')
        assert isinstance(response, Manga)
        assert response.name == 'The Demon King Who Lost His Job'

    def test_chapters(self):
        response = TsukiProvider().getChapters(9987)
        assert len(response) > 0
        for ch in response:
            assert isinstance(ch, Chapter)
        
    def test_getPages(self):
        response = TsukiProvider().getPages(397649)
        assert len(response.pages) > 0
        assert isinstance(response, Pages)
