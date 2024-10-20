from core.providers.infra.template.manga_reader_cms import MangaReaderCms

class TsundokuProvider(MangaReaderCms):
    name = 'Tsundokus'
    lang = 'pt-Br'
    domain = ['tsundoku.com.br']

    def __init__(self):
        super().__init__()
        self.url = 'https://tsundoku.com.br'
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'div#chapterlist ul li'
        self.query_pages = 'div#readerarea img'
        self.query_title_for_uri = 'h1.entry-title'
    