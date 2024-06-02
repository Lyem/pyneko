import os
import re
import ast
import math
from io import BytesIO
from typing import List
from pathlib import Path
from zipfile import ZipFile
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga
from core.download.domain.dowload_entity import Chapter as DChapter

class ScanMadaraClone(Base):

    def __init__(self):
        self.url = None
    
    def getMangas(self) -> List[Manga]:
        response = Http.get(f'{self.url}/todas-as-obras')
        soup = BeautifulSoup(response.content, 'html.parser')
        tags = soup.find_all('a', class_='titulo__comic__allcomics')
        list = []
        for tag in tags:
            list.append(Manga(id=tag.get('href'), name=tag.get_text()))
        return list
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        tags = soup.find_all('h1', class_='desc__titulo__comic')
        return Manga(id=link, name=tags[0].get_text())

    def getChapters(self, link: str) -> List[Chapter]:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        tags = soup.find_all('a', class_='link__capitulos')
        title = soup.find_all('h1', class_='desc__titulo__comic')[0].get_text()
        list = []
        for tag in tags:
            cap = tag.find('span', class_='numero__capitulo').get_text()
            list.append(Chapter(id=tag.get('href'), number=cap, name=title))
        return list
    
    def getPages(self, ch: Chapter) -> Pages:
        if not self.url in ch.id:
            ch.id = f'{self.url}{ch.id}'
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find('div', id='imageContainer')
        scripts = str(scripts.find_all('script')[1])
        match = re.search(r'const\s+urls\s*=\s*(\[.*?\]);', str(scripts), re.DOTALL)
        urls = ast.literal_eval(match.group(1))
        list = []
        for url in urls:
            list.append(f'{self.url}{url}')
        return Pages(id=ch.id, number=ch.number, name=ch.name, pages=list)

        
    
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        title = (pages.name[:20]) if len(pages.name) > 20 else pages.name
        title = re.sub('[^a-zA-Z0-9&_áàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ-]', '', title)
        path = os.path.join(os.getcwd(), 'mangas',
                            str(title), str(pages.number))
        os.makedirs(path, exist_ok=True)
        files = []
        page_number = 0
        for i, page in enumerate(pages.pages):
            response = Http.get(page, headers={'referer': f'{self.url}'})

            zip_content = BytesIO(response.content)

            with ZipFile(zip_content) as zip_file:
                for file_name in zip_file.namelist():
                    if not file_name.endswith('.s'):
                        page_number += 1
                        with zip_file.open(file_name) as file:
                            content = file.read()
                            if not os.path.exists(path):
                                os.makedirs(path)
                            file_path = os.path.join(path, f"%03d.webp" % page_number)
                            files.append(file_path)
                            Path(file_path).write_bytes(content)

            if fn != None:
                fn(math.ceil(i * 100)/len(pages.pages))
            
        if fn != None:
            fn(math.ceil(len(pages.pages) * 100)/len(pages.pages))
        
        return DChapter(pages.number, files)