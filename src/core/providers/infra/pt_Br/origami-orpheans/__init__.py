from core.providers.infra.template.manga_reader_cms import MangaReaderCms

class OrigamiOrpheansProvider(MangaReaderCms):
    name = 'Origami Orpheans'
    lang = 'pt_Br'
    domain = ['origami-orpheans.com']

    def __init__(self):
        super().__init__()
        self.url = 'https://origami-orpheans.com/manga/kono-healer-mendokusai/'
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'div#chapterlist > ul li a'
        self.query_pages = 'div#readerarea img'
        self.query_title_for_uri = 'h1.entry-title'