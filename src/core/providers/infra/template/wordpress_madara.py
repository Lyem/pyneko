import re
import json
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.__seedwork.infra.http.contract.http import Response
from core.providers.domain.entities import Chapter, Pages, Manga
from urllib.parse import urljoin, urlencode, urlparse, urlunparse, parse_qs

class WordPressMadara(Base):
    def __init__(self):
        self.url = None
        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div[class="page-break no-gaps"]'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'

    def getMangas(self) -> List[Manga]:
        manga_list = []
        page = 0
        while True:
            mangas = self._get_mangas_from_page(page)
            if mangas:
                manga_list.extend(mangas)
                page += 1
            else:
                break
        return manga_list

    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        data = soup.select(self.query_title_for_uri)
        element = data.pop()
        title = element['content'].strip() if 'content' in element.attrs else element.text.strip()
        return Manga(id=link, name=title)

    def getChapters(self, id: str) -> List[Chapter]:
        uri = urljoin(self.url, id)
        response = Http.get(uri)
        soup = BeautifulSoup(response.content, 'html.parser')
        data = soup.select(self.query_title_for_uri)
        element = data.pop()
        title = element['content'].strip() if 'content' in element.attrs else element.text.strip()
        dom = soup.select('body')[0]
        data = dom.select(self.query_chapters)
        placeholder = dom.select_one(self.query_placeholder)
        if placeholder:
            try:
                data = self._get_chapters_ajax(id)
            except Exception:
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

        return chs

    def getPages(self, id: str) -> Pages:
        uri = urljoin(self.url, id)
        uri = self._add_query_params(uri, {'style': 'list'})
        response = Http.get(uri)
        soup = BeautifulSoup(response.content, 'html.parser')
        data = soup.find_all('div', class_='page-break no-gaps')
        if not data:
            uri = self._remove_query_params(uri, ['style'])
            response = Http.get(uri)
            soup = BeautifulSoup(response.content, 'html.parser')
            data = soup.select(self.query_pages)
        
        script_tag = soup.find('script', type='application/ld+json')
        json_data = json.loads(script_tag.string)
        headline = json_data.get('headline')
        chapter_heading = soup.find('h1', id='chapter-heading').text.replace(headline, '').strip()

        list = [] 
        for el in data:
            list.append(self._process_page_element(el, uri))
        number = re.findall(r'\d+', chapter_heading)[0]
        return Pages(id, number, headline, list)

    def _create_manga_request(self, page):
        form = {
            'action': 'madara_load_more',
            'template': 'madara-core/content/content-archive',
            'page': page,
            'vars[paged]': '0',
            'vars[post_type]': 'wp-manga',
            'vars[posts_per_page]': '250'
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'x-referer': self.url
        }
        request_url = urljoin(self.url, f'{self.path}/wp-admin/admin-ajax.php')
        return Http.post(request_url, data=urlencode(form), headers=headers)

    def _fetch_dom(self, response: Response, query: str):
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.select(query)

    def _get_mangas_from_page(self, page):
        response = self._create_manga_request(page)
        data = self._fetch_dom(response, self.query_mangas)
        return [Manga(id=self.get_root_relative_or_absolute_link(el, response.url), name=el.text.strip()) for el in data]

    def _get_chapters_ajax_old(self, data_id):
        uri = urljoin(self.url, f'{self.path}/wp-admin/admin-ajax.php')
        response = Http.post(uri, data=f'action=manga_get_chapters&manga={data_id}', headers={
            'content-type': 'application/x-www-form-urlencoded',
            'x-referer': self.url
        })
        data = self._fetch_dom(response, self.query_chapters)
        if data:
            return data
        else:
            raise Exception('No chapters found (old ajax endpoint)!')

    def _get_chapters_ajax(self, manga_id):
        uri = urljoin(self.url, f'{manga_id}ajax/chapters/')
        response = Http.post(uri)
        data = self._fetch_dom(response, self.query_chapters)
        if data:
            return data
        else:
            raise Exception('No chapters found (new ajax endpoint)!')

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
    

