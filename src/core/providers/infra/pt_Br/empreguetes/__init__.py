import re
import math
import asyncio
from urllib import request
import nodriver as uc
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga
import json

class EmpreguetesProvider(Base):
    name = 'Empreguetes'
    lang = 'pt_Br'
    domain = ['novo.empreguetes.site']

    def __init__(self) -> None:
        self.base = 'https://api.sussytoons.wtf'
        self.CDN = 'https://cdn.sussytoons.site'
        self.old = 'https://oldi.sussytoons.site/wp-content/uploads/WP-manga/data/'
        self.chapter = 'https://novo.empreguetes.site/capitulos'
        self.webBase = 'https://www.sussytoons.wtf'
        self.cookies = [{'sussytoons-terms-accepted', 'true'}]
    
    def getManga(self, link: str) -> Manga:
        match = re.search(r'/obra/(\d+)', link)
        id_value = match.group(1)
        response = Http.get(f'{self.base}/obras/{id_value}').json()
        title = response['resultado']['obr_nome']
        return Manga(link, title)

    def getChapters(self, id: str) -> List[Chapter]:
        try:
            match = re.search(r'/obra/(\d+)', id)
            id_value = match.group(1)
            response = Http.get(f'{self.base}/obras/{id_value}').json()
            title = response['resultado']['obr_nome']
            list = []
            for ch in response['resultado']['capitulos']:
                list.append(Chapter([id_value, ch['cap_id']], ch['cap_nome'], title))
            return list
        except Exception as e:
            print(e)
    
    def getPages(self, ch: Chapter) -> Pages:
        try:
            if not hasattr(ch, 'id') or not isinstance(ch.id, (list, tuple)) or len(ch.id) < 2:
                raise ValueError("ch.id must be a list/tuple with at least 2 elements")
            if not hasattr(ch, 'number') or not isinstance(ch.number, str):
                raise ValueError("ch.number must be a valid string")
            if not hasattr(ch, 'name'):
                raise ValueError("ch.name must be defined")
            if not hasattr(self, 'CDN') or not self.CDN:
                raise ValueError("self.CDN must be defined and non-empty")
            if not hasattr(self, 'chapter') or not self.chapter:
                raise ValueError("self.chapter must be defined and non-empty")

            chapter_url = f"{self.chapter}/{ch.id[1]}"
            response = Http.get(chapter_url)
            if response.status not in range(200, 300):
                raise RuntimeError(f"Failed to fetch chapter data: {response.status} - {chapter_url}")

            image_urls = []
            attempts = 0
            current = 1
            zero_qt = 1
            max_zero_qt = 3
            image_formats = ['jpg', 'webp', 'png']
            current_format_idx = 0

            chapter_number_parts = ch.number.split(' ')
            if len(chapter_number_parts) < 2:
                raise ValueError(f"Invalid chapter number format: {ch.number}")
            chapter_number = chapter_number_parts[1]

            while True:
                url = f"{self.CDN}/scans/3/obras/{ch.id[0]}/capitulos/{chapter_number}/{current:0{zero_qt}d}.{image_formats[current_format_idx]}"
                try:
                    request_image = Http.get(url)
                except Exception as req_err:
                    print(f"Request failed for {url}: {req_err}")
                    request_image = None

                if request_image is None or request_image.status not in range(200, 300):
                    if zero_qt < max_zero_qt:
                        zero_qt += 1
                        continue
                    else:
                        current_format_idx += 1
                        zero_qt = 1
                        if current_format_idx >= len(image_formats):
                            break
                        continue

                    image_urls.append(url)
                    current += 1
                    zero_qt = 1
                    current_format_idx = 0

            if not image_urls:
                raise RuntimeError("No valid image URLs found")

            return Pages(ch.id, ch.number, ch.name, image_urls)

        except Exception as e:
            print(f"Error in getPages: {str(e)}")
            raise