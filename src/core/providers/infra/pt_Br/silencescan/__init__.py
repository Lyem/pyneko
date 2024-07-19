from core.providers.infra.template.manga_reader_cms import MangaReaderCms

class SilencescanProvider(MangaReaderCms):
    name = 'silencescan'
    icon = 'https://i.imgur.com/QRjE79s.png'
    icon_hash = 'd/iFDQIoqraAa360R1NPCZWlHiugekWiJw'
    lang = 'pt-Br'
    domain = 'silencescan.com.br'

    def __init__(self):
        super().__init__()
        self.url = 'https://silencescan.com.br'
        self.path = '/'

        self.query_mangas = 'ul.manga-list li a'
        self.query_chapters = 'div#chapterlist ul li'
        self.query_pages = 'div#readerarea img'
        self.query_title_for_uri = 'h1.entry-title'
    