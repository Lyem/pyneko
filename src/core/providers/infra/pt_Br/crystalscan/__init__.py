from core.providers.infra.template.wordpress_etoshore_manga_theme import WordpressEtoshoreMangaTheme

class CrystalScanProvider(WordpressEtoshoreMangaTheme):
    name = 'Crystal Scan'
    lang = 'pt_Br'
    domain = ['crystalcomics.com']

    def __init__(self) -> None:
        self.get_title = 'h1'
        self.get_chapters_list = 'div.list-box.chapter-list'
        self.chapter = 'li.language-BR > a'
        self.get_chapter_number = 'div.title'
        self.get_div_page = 'div.chapter-image-content'
        self.get_pages = 'noscript > img'
