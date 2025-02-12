import os
import cv2
import json
import nodriver as uc
from time import sleep
from typing import List
from pathlib import Path
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Chapter, Pages, Manga

class SlimeReadProvider(Base):
    name = 'Slime Read'
    lang = 'pt-Br'
    domain = ['slimeread.com']

    def __init__(self) -> None:
        self.base = 'https://slimeread.com'
        self.api = 'https://carnaval.slimeread.com:8443'
        ua = UserAgent()
        user = ua.chrome
        self.headers = {'origin': 'slimeread.com','referer': f'{self.base}', 'User-Agent': user}
        self.cdns = ['https://cdn2.slimeread.com/', 'https://cdn.slimeread.com/', 'https://black.slimeread.com/', 'https://objects.slimeread.com/']
    
    def getManga(self, link: str) -> Manga:
        id = link.split('/')[4]
        page = self.getPageContent(f'{self.base}/manga/{id}')
        soup = BeautifulSoup(page, 'html.parser')
        title = soup.select_one('h2.tw-tv.tw-zj.transition.tw-lp.tw-ey.tw-iu')
        return Manga(id, title.get_text())

    def _is_json(self, texto):
        try:
            json.loads(texto)
            return True
        except json.JSONDecodeError:
            return False
    
    def getPageContent(self, domain: str, background = False) -> any:
        content= ''
        async def get_script_result():
            nonlocal content
            browser = await uc.start(
                browser_args=[
                    '--window-size=600,600', 
                    f'--app={domain}',
                    '--disable-extensions', 
                    '--disable-popup-blocking'
                ],
                browser_executable_path=None,
                headless=background
            )
            page = await browser.get(domain)
            data = []
            while len(data) == 0:
                page_content = await page.get_content()
                soup = BeautifulSoup(page_content, 'html.parser')
                data = soup.select('h2.tw-tv.tw-zj.transition.tw-lp.tw-ey.tw-iu')
                # data = soup.select('h2.tw-tv.tw-zj.transition.tw-lp.tw-ey.tw-iu')

            content = page_content
            browser.stop()
        uc.loop().run_until_complete(get_script_result())
        return content

    def getChapters(self, id: str) -> List[Chapter]:
        list = []
        response = Http.get(f'{self.api}/book_cap_units_all?manga_id={id}', headers=self.headers)
        if(not self._is_json(response.content)):
            chs = BeautifulSoup(response.content, 'html.parser')
            pre_tag_content = chs.find('pre').text
            array = json.loads(pre_tag_content)
        else:
            array = response.json()
        page = self.getPageContent(f'{self.base}/manga/{id}')
        list = []
        soup = BeautifulSoup(page, 'html.parser')
        title = soup.select_one('h2.tw-tv.tw-zj.transition.tw-lp.tw-ey.tw-iu')
        for chapter in array:
            value = chapter['btc_cap'] + 1
            if value.is_integer():
                formatted_cap = f"{int(value)}"
            else:
                formatted_cap = f"{value:.1f}" 
            list.append(Chapter(f'{id}/{chapter['btc_cap']}', formatted_cap, title.get_text()))
        return list

    def getPages(self, ch: Chapter) -> Pages:
        list = []
        ids = ch.id.split('/')
        response = Http.get(f'{self.api}/book_cap_units?manga_id={ids[0]}&cap={ids[1]}', headers=self.headers)
        if(not self._is_json(response.content)):
            pages = BeautifulSoup(response.content, 'html.parser')
            pre_tag_content = pages.find('pre').text
            api_content = json.loads(pre_tag_content)
        else:
            api_content = response.json()
        cdn_selected = ''
        for data in api_content[0]['book_temp_cap_unit']:
            if(data['btcu_image'] != 'folders/pagina_inicial.png' and data['btcu_image'] != 'folders/pagina_final.png'):
                if data['btcu_provider_host'] == 5:
                    cdn_selected = self.cdns[2]
                elif data['btcu_provider_host'] == 3:
                    cdn_selected = self.cdns[3]
                elif data['btcu_provider_host'] == None:
                    cdn_selected = self.cdns[3]
                else:
                    cdn_selected = self.cdns[1]
                list.append(f'{cdn_selected}{data['btcu_image']}')
        return Pages(ch.id, ch.number, ch.name, list)
    
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
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= 0.8:
            y_cut = max_loc[1] + h  # Corta abaixo do template encontrado
            img_cropped = img[y_cut:, :]
            cv2.imwrite(output_path, img_cropped)
            return True
        
        return False
    
    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        if headers is None:
            headers = self.headers
        else:
            headers = headers | self.headers

        downloaded_pages = DownloadUseCase().execute(
            pages=pages, 
            fn=fn, 
            headers=headers, 
            cookies=cookies
        )

        # Lista de templates de marca a serem testados
        marks = ['mark1.png']  # Ajuste com seus arquivos
        marks_path = os.path.join(Path(__file__).parent, 'templates')  # Pasta com as marcas

        # Processar cada imagem baixada
        for page_path in downloaded_pages.files:
            for mark in marks:
                template_path = os.path.join(marks_path, mark)
                if self.removeMark(
                    img_path=page_path,
                    template_path=template_path,
                    output_path=page_path  # Sobrescreve a imagem original
                ):
                    break  # Para de testar templates se um for encontrado

        return downloaded_pages

if __name__ == "__main__":
    manga = SlimeReadProvider().getManga('https://slimeread.com/manga/545/a-caixa-de-joias-da-princesa')
    sleep(20)
    chps = SlimeReadProvider().getChapters(manga.id)
    pages = SlimeReadProvider().getPages(chps[0])
    print(pages)


