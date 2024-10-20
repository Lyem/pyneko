from core.providers.infra.template.wordpress_madara import WordPressMadara

class HotCabaretScanProvider(WordPressMadara):
    name = 'Hot Cabaret Scan'
    lang = 'pt_Br'
    domain = ['hotcabaretscan.com']

    def __init__(self):
        self.url = 'https://hotcabaretscan.com/'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break.no-gaps'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'