from core.providers.infra.template.wordpress_madara import WordPressMadara
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Chapter, Pages
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import base64

class SussyScanProvider(WordPressMadara):
    name = 'manhastro'
    icon = 'https://i.imgur.com/ycuyRsy.png'
    icon_hash = 'T3mBA4AkUz9sptRplgCb9VU7iHiQiYc'
    lang = 'pt-Br'
    domain = 'manhastro.com'

    def __init__(self):
        self.url = 'https://manhastro.com/'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break.no-gaps'
        self.query_title_for_uri = 'div.post-content > h2'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'
    
    def getPages(self, ch: Chapter) -> Pages:
        uri = urljoin(self.url, ch.id)
        uri = self._add_query_params(uri, {'style': 'list'})
        response = Http.get(uri)
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find('script', text=lambda text: text and 'var imageLinks =' in text)
        script_text = script_tag.string
    
        start_index = script_text.find('[')
        end_index = script_text.find(']')
        if start_index != -1 and end_index != -1:
            image_links_text = script_text[start_index:end_index+1]
        
        image_links = eval(image_links_text)
        decoded_links = list(map(lambda image: base64.b64decode(image).decode('utf-8'), image_links))

        return Pages(ch.id, ch.number, ch.name, decoded_links)
