from core.providers.infra.template.manga_reader_cms import MangaReaderCms

class HiveToonProvider(MangaReaderCms):
    name = 'Hive Toons'
    lang = 'en'
    domain = ['hivetoon.com']

    def __init__(self):
        super().__init__()
        self.url = 'https://hivetoon.com/'
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'ul.clstyle li a'
        self.query_pages = 'div#readerarea img'
        self.query_title_for_uri = 'h1.entry-title'