from core.providers.infra.template.wordpress_madara import WordPressMadara

class GDScansProvider(WordPressMadara):
    name = 'GD Scans'
    lang = 'en'
    domain = ['gdscans.com']

    def __init__(self):
        self.url = 'https://gdscans.com/'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break.no-gaps'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'