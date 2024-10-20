# import re
# import json
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# from core.__seedwork.infra.http import Http
# from core.providers.domain.entities import Chapter, Pages
from core.providers.infra.template.wordpress_madara import WordPressMadara

class HikariScanProvider(WordPressMadara):
    name = 'Hikari Scan'
    lang = 'pt-Br'
    domain = ['hikariscan.org']

    def __init__(self):
        super().__init__()
        self.url = 'https://hikariscan.org'
        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'

# from core.providers.infra.template.manga_reader_cms import MangaReaderCms

# class HikariScanProvider(MangaReaderCms):
#     name = 'Hikari Scan'
#     icon = 'https://i.imgur.com/QRjE79s.png'
#     icon_hash = 'd/iFDQIoqraAa360R1NPCZWlHiugekWiJw'
#     lang = 'pt-Br'
#     domain = 'hikariscan.org'

#     def __init__(self):
#         super().__init__()
#         self.url = 'https://hikariscan.org'
#         self.path = '/'

#         self.query_mangas = 'ul.manga-list li a'
#         self.query_chapters = 'div#chapterlist ul li'
#         self.query_pages = 'div#readerarea img'
#         self.query_title_for_uri = 'h1.entry-title'
    
#     def getPages(self, ch: Chapter) -> Pages:
#         response = Http.get(urljoin(self.url, ch.id))
#         soup = BeautifulSoup(response.content, 'html.parser')
#         script_tags = soup.find_all('script')
#         pages = []
#         for script in script_tags:
#             if script.string and "ts_reader.run" in script.string:
#                 pattern = re.search(r'ts_reader\.run\((\{.*\})\);', script.string, re.DOTALL)
                
#                 if pattern:
#                     json_data = json.loads(pattern.group(1))
                    
#                     images = json_data['sources'][0]['images']
                    
#                     for image_url in images:
#                         pages.append(image_url)
#                 break
#         return Pages(id=ch.id, number=ch.number, name=ch.name, pages=pages)