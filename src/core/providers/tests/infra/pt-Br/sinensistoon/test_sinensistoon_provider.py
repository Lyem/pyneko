from core.providers.infra.pt_Br.sinensistoon import SinensistoonProvider
from core.providers.domain.entities import Chapter, Pages, Manga

class TestSinensistoonProvider:
    # def test_mangas(self):
    #     response = SinensistoonProvider().getMangas()
    #     assert len(response) > 0
    #     for manga in response:
    #         assert isinstance(manga, Manga)

    def test_manga(self):
        response = SinensistoonProvider().getManga('https://sinensistoon.com/serena1/')
        assert isinstance(response, Manga)
        assert response.name == 'Serena'

    # def test_chapters(self):
    #     response = SinensistoonProvider().getChapters('https://sinensistoon.com/serena1/')
    #     assert len(response) > 0
    #     for ch in response:
    #         assert isinstance(ch, Chapter)
        
    # def test_getPages(self):
    #     response = Sinensistoon().getPages('https://sinensistoon.com/serena1/74/')
    #     assert len(response.pages) > 0
    #     assert isinstance(response, Pages)
