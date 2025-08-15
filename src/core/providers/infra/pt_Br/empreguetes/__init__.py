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
    domain = ['empreguetes.xyz']

    def __init__(self) -> None:
        self.base = 'https://api.sussytoons.wtf'
        self.CDN = 'https://cdn.sussytoons.site'
        self.old = 'https://oldi.sussytoons.site/wp-content/uploads/WP-manga/data/'
        self.chapter = 'https://empreguetes.xyz/capitulo'
        self.webBase = 'https://www.sussytoons.wtf'
        self.cookies = [{'sussytoons-terms-accepted', 'true'}]
    
    def getManga(self, link: str) -> Manga:
        match = re.search(r'/obra/(\d+)', link)
        id_value = match.group(1)
        response = Http.get(f'{self.base}/obras/{id_value}', headers={'scan-id': 'empreguetes.xyz'}).json()
        title = response['resultado']['obr_nome']
        return Manga(link, title)

    def getChapters(self, id: str) -> List[Chapter]:
        try:
            match = re.search(r'/obra/(\d+)', id)
            id_value = match.group(1)
            response = Http.get(f'{self.base}/obras/{id_value}', headers={'scan-id': 'empreguetes.xyz'}).json()
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
                raise ValueError("ch.id deve ser uma lista/tupla com pelo menos 2 elementos")
            if not hasattr(ch, 'number') or not isinstance(ch.number, str):
                raise ValueError("ch.number deve ser uma string válida")
            if not hasattr(ch, 'name'):
                raise ValueError("ch.name deve estar definido")
            if not hasattr(self, 'CDN') or not self.CDN:
                raise ValueError("self.CDN deve estar definido e não vazio")
            if not hasattr(self, 'chapter') or not self.chapter:
                raise ValueError("self.chapter deve estar definido e não vazio")

            chapter_number_parts = ch.number.split(' ')
            if len(chapter_number_parts) < 2:
                raise ValueError(f"Formato de número de capítulo inválido: {ch.number}")
            chapter_number = chapter_number_parts[1]

            chapter_url = f"{self.chapter}/{ch.id[1]}"
            response = Http.get(chapter_url, headers={'scan-id': 'empreguetes.xyz'})
            if response.status not in range(200, 300):
                raise RuntimeError(f"Failed to fetch chapter data: {response.status} - {chapter_url}")

            base_url = f"{self.CDN}/scans/3/obras/{ch.id[0]}/capitulos/{chapter_number}/"

            format_functions = [
                lambda n: str(n),      
                lambda n: f"{n:02d}",  
                lambda n: f"{n:03d}"     
            ]

            suffixes = ["", "_copiar", " (1) final copiar"]
            extensions = ["jpg", "webp", "png"]

            fixed_fmt = None
            fixed_suff = None
            fixed_ext = None
            found_first = False

            for fmt in format_functions:
                for suff in suffixes:
                    for ext in extensions:
                        page_str = fmt(1)
                        filename = f"{page_str}{suff}.{ext}"
                        url = base_url + filename
                        try:
                            response = Http.get(url, headers={'scan-id': 'empreguetes.xyz'})
                            if response.status in range(200, 300):
                                fixed_fmt = fmt
                                fixed_suff = suff
                                fixed_ext = ext
                                found_first = True
                                break
                        except Exception as e:
                            print(f"Falha na requisição para {url}: {e}")
                    if found_first:
                        break
                if found_first:
                    break

            if not found_first:
                raise RuntimeError("Nenhuma URL de imagem válida encontrada para a página 1")

            image_urls = []
            current = 1
            max_pages = 1000 

            while len(image_urls) < max_pages:
                page_str = fixed_fmt(current)
                filename = f"{page_str}{fixed_suff}.{fixed_ext}"
                url = base_url + filename
                try:
                    response = Http.get(url, headers={'scan-id': 'empreguetes.xyz'})
                    if response.status in range(200, 300):
                        image_urls.append(url)
                        current += 1
                    else:
                        break
                except Exception as e:
                    print(f"Falha na requisição para {url}: {e}")
                    break

            if not image_urls:
                raise RuntimeError("Nenhuma URL de imagem válida encontrada")
            return Pages(ch.id, ch.number, ch.name, image_urls)

        except Exception as e:
            print(f"Erro em getPages: {str(e)}")
            raise