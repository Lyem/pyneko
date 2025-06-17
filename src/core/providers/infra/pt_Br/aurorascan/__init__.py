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


class AurorascanProvider(Base):
    name = 'Aurora Scan'
    lang = 'pt_Br'
    domain = ['aurorascan.net']

    def __init__(self) -> None:
        self.base = 'https://api.sussytoons.wtf'
        self.CDN = 'https://cdn.sussytoons.site'
        self.old = 'https://oldi.sussytoons.site/wp-content/uploads/WP-manga/data/'
        self.chapter = 'https://aurorascan.net/capitulo'
        self.webBase = 'https://www.sussytoons.wtf'
        self.cookies = [{'sussytoons-terms-accepted', 'true'}]
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('title')
        return Manga(link, title.get_text())
    
    def extract_json_object(self, text, key):
        inicio = text.find(f'"{key}":')
        if inicio == -1:
            return None

        inicio_json = text.find('{', inicio)
        if inicio_json == -1:
            return None

        contador = 0
        fim_json = inicio_json

        for i, char in enumerate(text[inicio_json:], start=inicio_json):
            if char == '{':
                contador += 1
            elif char == '}':
                contador -= 1
                if contador == 0:
                    fim_json = i + 1
                    break

        json_str = text[inicio_json:fim_json]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print("Erro ao decodificar JSON:", e)
            print("JSON bruto:", json_str)
            return None
    
    def getChapters(self, id: str) -> List[Chapter]:
        try:
            match = re.search(r'/obra/(\d+)', id)
            id_value = match.group(1)
            response = Http.get(id)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.select_one('title')
            scripts = soup.find_all('script')
            target_script = None
            for script in scripts:
                if script.string and 'cap_id' in script.string:
                    print(f"Script encontrado")
                    target_script = script.string
                    break
            match = re.search(r'self\.__next_f\.push\(\[1,"(5:.*?)"\]\)', target_script, re.DOTALL)
            list = []
            if not match:
                print("Não foi possível extrair a string JSON embutida.")
            else:
                json_raw = match.group(1)

                escape = json_raw.encode().decode("unicode_escape")

                result = self.extract_json_object(escape, "resultado")
                
                if result:
                    for cap in result['capitulos']:
                        list.append(Chapter([id_value, cap['cap_id']], cap['cap_nome'].encode('latin1').decode('utf-8'), title.get_text()))
                else:
                    print("Não foi possível extrair o JSON de capítulos.")
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
            response = Http.get(chapter_url)
            if response.status not in range(200, 300):
                raise RuntimeError(f"Failed to fetch chapter data: {response.status} - {chapter_url}")

            base_url = f"{self.CDN}/scans/4/obras/{ch.id[0]}/capitulos/{chapter_number}/"

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
                            response = Http.get(url)
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
                    response = Http.get(url)
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
