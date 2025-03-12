from core.providers.infra.template.yushuke_theme import YushukeTheme

class PlumaComicsProvider(YushukeTheme):
    name = 'Pluma Comics'
    lang = 'pt_Br'
    domain = ['new.plumacomics.cloud']

    def __init__(self) -> None:
        self.url = 'https://new.plumacomics.cloud'
        self.chapters_api = f'{self.url}/ajax/lzmvke.php?'
        
        self.title = 'div.manga-title-row h1'
        self.manga_id_selector = "button#CarregarCapitulos"
        self.chapter_item_selector = 'a.chapter-item'
        self.chapter_number_selector = 'span.capitulo-numero'
        self.chapter_views_selector = 'span.chapter-views'
        self.pages_selector = "div.select-nav + * picture"
        self.id_manga = 'data-manga-id'
        self.image_selector = "img"