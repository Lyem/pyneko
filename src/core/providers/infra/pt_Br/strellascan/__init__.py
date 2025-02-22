import re
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Chapter
from core.providers.infra.template.blogger_cms import BloggerCms

class StrellaScanProvider(BloggerCms):
    name = 'Strella Scans'
    lang = 'pt_Br'
    domain = ['www.strellascan.xyz']

    def __init__(self) -> None:
        self.get_title = 'header h1'
        self.API_domain = 'www.strellascan.xyz'
        self.get_pages = 'div.separator a img'
    
    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one(self.get_title)
        cleaned_title = re.sub(r"[^\w\sáéíóúâêîôûãõçÁÉÍÓÚÂÊÎÔÛÃÕÇ]", "", title.get_text(strip=True))
        list = []
        response = Http.get(f'https://{self.API_domain}/feeds/posts/default/-/{cleaned_title}?alt=json&start-index=1&max-results=150').json()
        if response['feed']['entry']:
            for ch in response['feed']['entry']:
                if ch['link'][4]['href'] == id:
                    continue
                list.append(Chapter(ch['link'][4]['href'], ch['title']['$t'], title.get_text(strip=True)))
        return list


 
