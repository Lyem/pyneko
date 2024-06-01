from core.providers.infra.pt_Br.sussyscan import SussyScanProvider
from core.providers.domain.entities import Chapter, Pages, Manga

class TestSussyScanProvider:
    def test_mangas(self):
        response = SussyScanProvider().getMangas()
        assert len(response) > 0
        for manga in response:
            assert isinstance(manga, Manga)

    def test_manga(self):
        response = SussyScanProvider().getManga('https://sussyscan.com/manga/arquimago-streamer/')
        assert isinstance(response, Manga)
        assert response.name == 'Arquimago Streamer'

    def test_chapters(self):
        response = SussyScanProvider().getChapters('https://sussyscan.com/manga/arquimago-streamer/')
        assert len(response) > 0
        for ch in response:
            assert isinstance(ch, Chapter)
        
    def test_getPages(self):
        response = SussyScanProvider().getPages('https://sussyscan.com/manga/arquimago-streamer/capitulo-62/')
        assert len(response.pages) > 0
        assert isinstance(response, Pages)
