import re
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from urllib.parse import urlparse, parse_qs
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

class LoobytProvider(Base):
    name = 'Loobyt'
    lang = 'pt_Br'
    domain = ['www.loobyt.com']

    def __init__(self) -> None:
        self.base = 'https://www.loobyt.com/readme/'
    
    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1.hidden.text-3xl.font-bold')

        return Manga(link, title.get_text(strip=True))

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('h1.hidden.text-3xl.font-bold')
        get_id = soup.select_one('div.flex.items-center.justify-between a')
        url_parsed = urlparse(get_id.get('href'))
        params = parse_qs(url_parsed.query)
        id = params.get('pull', [None])[0]
        response = Http.get('https://www.loobyt.com/api/trpc/manga.getLiked,chapter.publicAllChapters?batch=1&input={"1":{"json":{"id":'+ f'"{id}"' +',"page":1,"limit":999999999999,"sort":"desc","search":""}}}').json()
        list = []
        for ch in response[1]['result']['data']['json']['chapters']:
            list.append(Chapter(f'{self.base}{ch['id']}', f'Capítulo {ch['number']}', title.get_text(strip=True)))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.select('body script')[10]
        print(scripts.get_text())
        cdn_pattern = r'https:\/\/cdn\.readmangas\.org\/[^"]+'
        list = re.findall(cdn_pattern, scripts.get_text())
        urls = [url.rstrip("\\") for url in list]
        return Pages(ch.id, ch.number, ch.name, urls)
