from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.domain.entities import Chapter
from core.providers.infra.template.blogger_cms import BloggerCms

class SafireScanProvider(BloggerCms):
    name = 'Safire Scans'
    lang = 'pt_Br'
    domain = ['www.safirescan.xyz']


    def __init__(self) -> None:
        self.get_title = 'header h1'
        self.API_domain = 'www.safirescan.xyz'
        self.get_pages = 'div.separator a img'

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one(self.get_title)
        get_sub_titles = soup.select_one('h1.my-2.text-2xl + p')
        sub_titles = get_sub_titles.get_text().split(',')
        list = []
        for sub_title in sub_titles:
            response = Http.get(f'https://{self.API_domain}/feeds/posts/default/-/{sub_title.strip('')}?alt=json&start-index=1&max-results=150').json()
            if response['feed']['entry']:
                for ch in response['feed']['entry']:
                    if ch['link'][4]['href'] == id:
                        continue
                    list.append(Chapter(ch['link'][4]['href'], ch['title']['$t'], title.get_text(strip=True)))
                break
        return list