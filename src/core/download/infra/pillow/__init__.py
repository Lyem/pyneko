import re
import os
import math
import base64
import tldextract
import pillow_avif
from PIL import Image
import nodriver as uc
from time import sleep
from io import BytesIO
from tinydb import TinyDB, where
from platformdirs import user_data_path
from core.__seedwork.infra.http import Http
from core.config.request_data import RequestData
from core.providers.domain.page_entity import Pages
from core.download.domain.dowload_entity import Chapter
from core.download.domain.dowload_repository import DownloadRepository
Image.MAX_IMAGE_PIXELS = 933120000

class PillowDownloadRepository(DownloadRepository):

    def download_cloudflare(self, pages: Pages,path: str ,fn=None) -> Chapter:
        data_path = user_data_path('pyneko')
        db_path = data_path / 'request.json'
        db = TinyDB(db_path)
        files = []
        async def get_cloudflare_cookie():
            nonlocal files
            nonlocal pages
            nonlocal path
            nonlocal fn

            extract = tldextract.extract(pages.pages[0])
            domain = f"{extract.domain}.{extract.suffix}"
            browser = await uc.start(
                browser_args=[
                    '--window-size=600,600', 
                    f'--app=https://{domain}',
                    '--disable-extensions', 
                    '--disable-popup-blocking'
                ],
                browser_executable_path=None,
                headless=False
            )
            page = await browser.get(f'https://{domain}')
            request_data = db.search(where('domain') == domain)
            if(len(request_data) > 0):
                re = RequestData.from_dict(request_data[0])
                print(re.cookies)
                await page.evaluate(f'document.cookie = "cf_clearance={re.cookies['cf_clearance']}; path=/; max-age=3600; secure; samesite=strict";')
                await page.reload()

            while(True):
                page_content = await page.get_content()
                if self.is_cloudflare_blocking(page_content):
                    sleep(1)
                else:
                    for i, page in enumerate(pages.pages):
                        fetch_content = await page.evaluate(f'''
                            fetch("{page}")''' + '''.then(response => response.arrayBuffer()).then(buffer => {
                                let binary = '';
                                let bytes = new Uint8Array(buffer);
                                let len = bytes.byteLength;
                                for (let i = 0; i < len; i++) {
                                    binary += String.fromCharCode(bytes[i]);
                                }
                                return btoa(binary);
                            });
                        ''', await_promise=True)
                        try:
                            img = Image.open(BytesIO(base64.b64decode(fetch_content)))
                            img.verify()
                            icc = img.info.get('icc_profile')
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            file = os.path.join(path, f"%03d.jpg" % page_number)
                            files.append(file)
                            img.save(file, quality=80, dpi=(72, 72), icc_profile=icc)
                        except:
                            file = os.path.join(path, f"%03d.jpg" % page_number)
                            files.append(file)
                            with open(file, 'wb') as archive:
                                archive.write(base64.b64decode(fetch_content))
                        if fn != None:
                            fn(math.ceil(i * 100)/len(pages.pages))
                        page_number += 1

                    if fn != None:
                        fn(math.ceil(len(pages.pages) * 100)/len(pages.pages))
                    break
            browser.stop()
        uc.loop().run_until_complete(get_cloudflare_cookie())
        return Chapter(pages.number, files)

    def download(self, pages: Pages, fn=None, headers=None, cookies=None) -> Chapter:
        title = (pages.name[:20]) if len(pages.name) > 20 else pages.name
        title = re.sub('[^a-zA-Z0-9&_áàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ-]', '', title)
        path = os.path.join(os.getcwd(), 'mangas', str(title), str(pages.number))
        os.makedirs(path, exist_ok=True)
        cloudflare = False

        response = Http.get(pages.pages[0], headers=headers, cookies=cookies)
        if(response.status == 403):
            cloudflare = True

        if not cloudflare:
            page_number = 1
            files = []
            for i, page in enumerate(pages.pages):
                response = Http.get(page, headers=headers, cookies=cookies)
                try:
                    img = Image.open(BytesIO(response.content))
                    img.verify()
                    icc = img.info.get('icc_profile')
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    file = os.path.join(path, f"%03d.jpg" % page_number)
                    files.append(file)
                    img.save(file, quality=80, dpi=(72, 72), icc_profile=icc)
                except:
                    if response.status == 200:
                        file = os.path.join(path, f"%03d.jpg" % page_number)
                        files.append(file)
                        with open(file, 'wb') as archive:
                            archive.write(response.content)
                if fn != None:
                    fn(math.ceil(i * 100)/len(pages.pages))
                page_number += 1

            if fn != None:
                fn(math.ceil(len(pages.pages) * 100)/len(pages.pages))

            return Chapter(pages.number, files)
        
        else:
            return self.download_cloudflare(pages, path, fn)
