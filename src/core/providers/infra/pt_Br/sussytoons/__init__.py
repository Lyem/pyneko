import re
import math
import asyncio
import nodriver as uc
from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga
import json

class NewSussyToonsProvider(Base):
    name = 'New Sussy Toons'
    lang = 'pt_Br'
    domain = ['new.sussytoons.site', 'www.sussyscan.com', 'www.sussytoons.site', 'www.sussytoons.wtf', 'sussytoons.wtf']

    def __init__(self) -> None:
        self.base = 'https://api.sussytoons.wtf'
        self.CDN = 'https://cdn.sussytoons.site'
        self.old = 'https://oldi.sussytoons.site/wp-content/uploads/WP-manga/data/'
        self.oldCDN = 'https://oldi.sussytoons.site/scans/1/obras'
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


    def get_Pages(self, id, sleep, background = False):
        async def get_Pages_driver():
            inject_script = """
            const mockResponse = {
                statusCode: 200,
                resultado: {
                    usr_id: 83889,
                    usr_nome: "White_Preto",
                    usr_email: "emailgay@gmail.com",
                    usr_nick: "emailgay",
                    usr_imagem: null,
                    usr_banner: null,
                    usr_moldura: null,
                    usr_criado_em: "2025-02-26 16:34:19.591",
                    usr_atualizado_em: "2025-02-26 16:34:19.591",
                    usr_status: "ATIVO",
                    vip_habilitado: true,
                    vip_habilitado_em: "2025-02-26 16:34:19.591",
                    vip_temporario_em: null,
                    vip_acaba_em: "2035-02-26 16:34:19.591",
                    usr_google_token: null,
                    scan: {
                        scan_id: 1,
                        scan_nome: "Sussy"
                    },
                    scan_id: 1,
                    tags: []
                }
            };

            // Intercepta todas as requisições para a API
            const originalFetch = window.fetch;
            window.fetch = async function(url, options) {
                if (url.includes('api.sussytoons.wtf/me')) {
                    return new Response(JSON.stringify(mockResponse), {
                        status: 200,
                        headers: {'Content-Type': 'application/json'}
                    });
                }
                return originalFetch(url, options);
            };
            """

            browser = await uc.start(
                browser_args=[
                    '--window-size=600,600', 
                    f'--app={id}',
                    '--disable-extensions', 
                    '--disable-popup-blocking'
                ],
                browser_executable_path=None,
                headless=background
            )
            page = await browser.get(id)
            await browser.cookies.set_all(self.cookies)
            
            await page.evaluate(inject_script)
            
            await asyncio.sleep(sleep)
            html = await page.get_content()
            browser.stop() 
            return html
        resultado = uc.loop().run_until_complete(get_Pages_driver())
        return resultado
    
    def getPages(self, ch: Chapter) -> Pages:
        images = []
        base_delay = 25  
        max_delay = 300 
        max_attempts = 5 
        attempt = 0

        while attempt < max_attempts:
            try:
                current_delay = min(base_delay * math.pow(2, attempt), max_delay)
                
                print(f"Attempt {attempt + 1} - Using {current_delay} seconds delay")
                
                html = self.get_Pages(
                    id=f'{self.webBase}/capitulo/{ch.id[1]}',
                    sleep=current_delay,
                    background=attempt > 1 
                )
                
                soup = BeautifulSoup(html, 'html.parser')
                images = [img.get('src') for img in soup.select('img.chakra-image.css-8atqhb')]
                
                if images:
                    print("Successfully fetched images")
                    break
                else:
                    print("No images found, retrying...")

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
            
            attempt += 1

        return Pages(ch.id, ch.number, ch.name, images)
