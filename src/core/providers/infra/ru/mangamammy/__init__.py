import subprocess
import re
import os
import math
from PIL import Image
from io import BytesIO
from core.config.img_conf import get_config
from core.__seedwork.infra.http import Http
from core.providers.domain.page_entity import Pages
from core.download.domain.dowload_entity import Chapter
from core.download.domain.dowload_repository import DownloadRepository
from core.__seedwork.infra.utils.sanitize_folder import sanitize_folder_name
Image.MAX_IMAGE_PIXELS = 933120000
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.__seedwork.infra.http.contract.http import Response
from core.providers.domain.entities import Chapter, Pages, Manga
from core.providers.infra.template.wordpress_madara import WordPressMadara
from urllib.parse import urljoin, urlencode, urlparse, urlunparse, parse_qs

class MangaMammyProvider(WordPressMadara):
    name = 'Manga Mammy'
    lang = 'ru'
    domain = ['mangamammy.ru']

    def __init__(self):
        self.url = 'https://mangamammy.ru'

        self.path = ''
        self.headers = {'Accept-Encoding': 'gzip, deflate, br, zstd'}
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'

    def curl_request(self, request, method, data=None, as_text=True):
        command = [
            "curl",
            request,
            "--compressed",
            "-X", method,
            "-H", "Accept-Encoding: gzip, deflate, br, zstd",
        ]
        
        if data is not None:
            command.extend(["--data-raw", str(data)])
        
        if as_text:
            result = subprocess.run(command, capture_output=True, text=True)
        else:
            result = subprocess.run(command, capture_output=True)
        
        return result
    
    def getManga(self, link: str) -> Manga:
        response = self.curl_request(link, 'GET')
        soup = BeautifulSoup(response.stdout, 'html.parser')
        data = soup.select(self.query_title_for_uri)
        element = data.pop()
        title = element['content'].strip() if 'content' in element.attrs else element.text.strip()
        return Manga(id=link, name=title)

    def getChapters(self, id: str) -> List[Chapter]:
        uri = urljoin(self.url, id)
        response = self.curl_request(uri, 'GET')
        soup = BeautifulSoup(response.stdout, 'html.parser')
        data = soup.select(self.query_title_for_uri)
        element = data.pop()
        title = element['content'].strip() if 'content' in element.attrs else element.text.strip()
        dom = soup.select('body')[0]
        data = dom.select(self.query_chapters)
        placeholder = dom.select_one(self.query_placeholder)
        if placeholder:
            try:
                data = self._get_chapters_ajax_old(placeholder['data-id'])
            except Exception:
                pass

        chs = []
        for el in data:
            ch_id = self.get_root_relative_or_absolute_link(el, uri)
            ch_number = el.text.strip()
            ch_name = title
            chs.append(Chapter(ch_id, ch_number, ch_name))

        chs.reverse()
        return chs

    def getPages(self, ch: Chapter) -> Pages:
        uri = urljoin(self.url, ch.id)
        uri = self._add_query_params(uri, {'style': 'list'})
        response = self.curl_request(uri, 'GET')
        soup = BeautifulSoup(response.stdout, 'html.parser')
        data = soup.select(self.query_pages)
        if not data:
            uri = self._remove_query_params(uri, ['style'])
            response = self.curl_request(uri, 'GET')
            soup = BeautifulSoup(response.stdout, 'html.parser')
            data = soup.select(self.query_pages)
        list = [] 
        for el in data:
            list.append(self._process_page_element(el, uri))

        number = re.findall(r'\d+\.?\d*', str(ch.number))[0]
        print(list)
        return Pages(ch.id, number, ch.name, list)

    def _fetch_dom(self, response: Response, query: str):
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.select(query)

    def _get_mangas_from_page(self, page):
        response = self._create_manga_request(page)
        data = self._fetch_dom(response, self.query_mangas)
        return [Manga(id=self.get_root_relative_or_absolute_link(el, response.url), name=el.text.strip()) for el in data]

    
    def _get_chapters_ajax_old(self, data_id):
        uri = urljoin(self.url, f'{self.path}/wp-admin/admin-ajax.php')
        response = self.curl_request(uri, data=f'action=manga_views&manga={data_id}')
        data = self._fetch_dom(response, self.query_chapters)
        if data:
            return data
        else:
            raise Exception('No chapters found (old ajax endpoint)!')


    def _process_page_element(self, element, referer):
        element = element.find('img') or element.find('image')
        src = element.get('data-url') or element.get('data-src') or element.get('srcset') or element.get('src')
        element['src'] = src
        if 'data:image' in src:
            return src.split()[0]
        else:
            uri = urlparse(self.get_absolute_path(element, referer))
            canonical = parse_qs(uri.query).get('src')
            if canonical and canonical[0].startswith('http'):
                uri = uri._replace(query='')
                uri = uri._replace(path=canonical[0])
            return self.create_connector_uri({'url': uri.geturl(), 'referer': referer})

    def _add_query_params(self, url, params):
        url_parts = list(urlparse(url))
        query = dict(parse_qs(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query, doseq=True)
        return urlunparse(url_parts)

    def _remove_query_params(self, url, params):
        url_parts = list(urlparse(url))
        query = dict(parse_qs(url_parts[4]))
        for param in params:
            query.pop(param, None)
        url_parts[4] = urlencode(query, doseq=True)
        return urlunparse(url_parts)

    def get_root_relative_or_absolute_link(self, element, base_url):
        href = element.get('href')
        return urljoin(base_url, href) if href else None

    def get_absolute_path(self, element, base_url):
        return urljoin(base_url, element['src'])

    def create_connector_uri(self, payload):
        return payload['url']
    
    def download(self, pages: Pages, fn=None, headers=None, cookies=None, timeout=None) -> Chapter:
        title = sanitize_folder_name(pages.name)
        config = get_config()
        img_path = config.save
        path = os.path.join(img_path, str(title), str(sanitize_folder_name(pages.number)))
        os.makedirs(path, exist_ok=True)
        img_format = config.img

        page_number = 1
        files = []
        for i, page in enumerate(pages.pages):
            response = self.curl_request(page, 'GET', as_text=False)
            try:
                img = Image.open(BytesIO(response.stdout))
                icc = img.info.get('icc_profile')
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                file = os.path.join(path, f"%03d{img_format}" % page_number)
                img.save(file, quality=100, dpi=(72, 72), icc_profile=icc)
                files.append(file)
            except Exception as e:
                print(f"<stroke style='color:green;'>[Downloading]:</stroke> <span style='color:red;'>Error</stroke> {e}")

            if fn != None:
                fn(math.ceil(i * 100)/len(pages.pages))
            page_number += 1

        if fn != None:
            fn(math.ceil(len(pages.pages) * 100)/len(pages.pages))

        return Chapter(pages.number, files)

    
        

