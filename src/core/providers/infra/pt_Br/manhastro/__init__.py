import os
import cv2
import base64
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Chapter, Pages
from core.download.application.use_cases import DownloadUseCase
from core.providers.infra.template.wordpress_madara import WordPressMadara

class ManhastroProvider(WordPressMadara):
    name = 'Manhastro'
    lang = 'pt-Br'
    domain = ['manhastro.com']

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
    
    def adjust_template_size(self, template, img):
        h_img, w_img = img.shape[:2]
        h_template, w_template = template.shape[:2]

        if h_template > h_img or w_template > w_img:
            scale_h = h_img / h_template
            scale_w = w_img / w_template
            scale = min(scale_h, scale_w)
            template = cv2.resize(template, (int(w_template * scale), int(h_template * scale)))

        return template
    
    def removeMark(self, img_path, template_path, output_path) -> bool:
        img = cv2.imread(img_path)
        template = cv2.imread(template_path)
        template = self.adjust_template_size(template, img)

        h, w = template.shape[:2]

        img_cropped = img[-h:, :]

        result = cv2.matchTemplate(img_cropped, template, cv2.TM_CCOEFF_NORMED)

        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= 0.8:
            img_without_mark = img[:-h, :]

            cv2.imwrite(output_path, img_without_mark)

            return True
        
        return False
    
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        pages = DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)
        marks = ['mark.jpg', 'mark2.jpg', 'mark3.jpg', 'mark4.jpg', 'mark5.jpg', 'mark6.jpg', 'mark7.jpg', 'mark8.jpg', 'mark9.jpg', 'mark10.jpg', 'mark11.jpg']
        for page in pages.files:
            for mark in marks:
                if self.removeMark(page, os.path.join(Path(__file__).parent, mark), page):
                    break
        return  pages
