from core.providers.infra.template.wordpress_madara import WordPressMadara

class HariMangaProvider(WordPressMadara):
    name = 'Hari Mangas'
    lang = 'en'
    domain = ['harimanga.me']

    def __init__(self):
        self.url = 'https://harimanga.me'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break.no-gaps'
        self.query_title_for_uri = 'div.post-title h1'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'