from core.providers.infra.template.manga_reader_cms import MangaReaderCms

class DrakeComicProvider(MangaReaderCms):
    name = 'Drake Scans'
    lang = 'en'
    domain = ['drakecomic.org']

    def __init__(self):
        super().__init__()
        self.url = 'https://drakecomic.org/'
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'div#chapterlist ul li'
        self.query_pages = 'div#readerarea img'
        self.query_title_for_uri = 'h1.entry-title'