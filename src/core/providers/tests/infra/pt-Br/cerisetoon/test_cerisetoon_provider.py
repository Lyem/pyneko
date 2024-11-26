from core.providers.infra.pt_Br.cerisescan import CeriseScanProvider
from core.providers.domain.entities import Chapter, Pages, Manga

response = CeriseScanProvider().getPages('https://cerisetoon.com/a-besta-domada-pela-vila/54/')
CeriseScanProvider().download(response)

class TestCerisetoonProvider:
    # def test_mangas(self):
    #     response = CerisetoonProvider().getMangas()
    #     assert len(response) > 0
    #     for manga in response:
    #         assert isinstance(manga, Manga)

    # def test_manga(self):
    #     response = CerisetoonProvider().getManga('https://cerisetoon.com/a-besta-domada-pela-vila/')
    #     assert isinstance(response, Manga)
    #     assert response.name == 'A Besta Domada pela Vilã'

    # def test_chapters(self):
    #     response = CerisetoonProvider().getChapters('https://cerisetoon.com/a-besta-domada-pela-vila/')
    #     assert len(response) > 0
    #     for ch in response:
    #         assert isinstance(ch, Chapter)
        
    def test_getPages(self):
        response = CeriseScanProvider().getPages('https://cerisetoon.com/a-besta-domada-pela-vila/54/')
        assert len(response.pages) > 0
        assert isinstance(response, Pages)
