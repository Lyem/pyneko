from core.providers.infra.template.manga_reader_cms import MangaReaderCms

class SssScanlatorProvider(MangaReaderCms):
    name = 'Sss Scanlator'
    lang = 'pt-Br'
    domain = 'sssscanlator.com.br'

    def __init__(self):
        super().__init__()
        self.url = 'https://sssscanlator.com.br'
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'div#chapterlist ul li'
        self.query_pages = 'div#readerarea img'
        self.query_title_for_uri = 'h1.entry-title'