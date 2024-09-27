import base64
import tldextract
import nodriver as uc
from time import sleep
from bs4 import BeautifulSoup
from tinydb import TinyDB, where
from platformdirs import user_data_path
from core.config.request_data import RequestData
from core.cloudflare.domain.request_entity import Request
from core.cloudflare.domain.bypass_repository import BypassRepository
from core.cloudflare.infra.nodriver.chrome import find_chrome_executable

data_path = user_data_path('pyneko')
db_path = data_path / 'request.json'
db = TinyDB(db_path)

class Cloudflare(BypassRepository):
    def is_cloudflare_blocking(self, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string if soup.title else ""
        if "Just a moment..." in title:
            return True
        
        if "Um momento…" in title:
            return True
        
        return False
    
    def is_cloudflare_time_out(self, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string if soup.title else ""
        if "Gateway time-out" in title:
            return True
        
        return False

    def bypass_cloudflare(self, url: str) -> Request:
        headers={}
        cookies={}
        async def get_cloudflare_cookie():
            nonlocal headers, cookies
            browser = await uc.start(
                browser_args=[
                    '--window-size=600,600', 
                    f'--app={url}',
                    '--disable-extensions', 
                    '--disable-popup-blocking'
                    '--no-sandbox'
                ],
                browser_executable_path=find_chrome_executable(),
            )
            page = await browser.get(url)
            agent = await page.evaluate('navigator.userAgent')
            headers = { 'user-agent': agent }
            while(True):
                page_content = await page.get_content()
                if self.is_cloudflare_blocking(page_content):
                    sleep(1)
                else:
                    break
            cookiesB = await browser.cookies.get_all()
            for cookie in cookiesB:
                if(cookie.name == 'cf_clearance'):
                    cookies = {'cf_clearance': cookie.value}
            browser.stop()
        uc.loop().run_until_complete(get_cloudflare_cookie())
        return Request(user_agent=headers, cloudflare_cookie_value=cookies)
    
    def bypass_cloudflare_no_capcha(self, url: str) -> str:
        content={}
        async def get_cloudflare_cookie():
            nonlocal content
            cloudflare = False
            extract = tldextract.extract(url)
            onlydomain = f"{extract.domain}.{extract.suffix}"
            browser = await uc.start(
                browser_args=[
                    '--window-size=600,600', 
                    f'--app={url}',
                    '--disable-extensions', 
                    '--disable-popup-blocking'
                ],
                browser_executable_path=None
            )
            page = await browser.get(url)
            request_data = db.search(where('domain') == onlydomain)
            if(len(request_data) > 0):
                re = RequestData.from_dict(request_data[0])
                await page.evaluate(f'document.cookie = "cf_clearance={re.cookies['cf_clearance']}; path=/; max-age=3600; secure; samesite=strict";')
                await page.reload()
            while(True):
                page_content = await page.get_content()
                if self.is_cloudflare_blocking(page_content):
                    cloudflare = True
                    sleep(1)
                else:
                    if cloudflare:
                        request_data = db.search(where('domain') == onlydomain)
                        if(len(request_data) > 0):
                            db.remove(where('domain') == onlydomain)
                        agent = await page.evaluate('navigator.userAgent')
                        headers = { 'user-agent': agent }
                        cookiesB = await browser.cookies.get_all()
                        cookies={}
                        for cookie in cookiesB:
                            if(cookie.name == 'cf_clearance'):
                                cookies = {'cf_clearance': cookie.value}
                        db.insert(RequestData(domain=onlydomain, headers=headers, cookies=cookies).as_dict())
                    content = page_content 
                    break
            browser.stop()
        uc.loop().run_until_complete(get_cloudflare_cookie())
        return content
    
    def bypass_cloudflare_no_capcha_fetch(self, domain: str, url: str, background = False) -> any:
        content={}
        async def get_cloudflare_cookie():
            nonlocal content
            cloudflare = False
            extract = tldextract.extract(domain)
            onlydomain = f"{extract.domain}.{extract.suffix}"
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
            request_data = db.search(where('domain') == onlydomain)
            if(len(request_data) > 0):
                re = RequestData.from_dict(request_data[0])
                await page.evaluate(f'document.cookie = "cf_clearance={re.cookies['cf_clearance']}; path=/; max-age=3600; secure; samesite=strict";')
                await page.reload()
            while(True):
                page_content = await page.get_content()
                fetch_content = await page.evaluate(f'''
                    fetch("{url}")''' + '''.then(response => response.arrayBuffer()).then(buffer => {
                        let binary = '';
                        let bytes = new Uint8Array(buffer);
                        let len = bytes.byteLength;
                        for (let i = 0; i < len; i++) {
                            binary += String.fromCharCode(bytes[i]);
                        }
                        return btoa(binary);
                    });
                ''', await_promise=True)
                if self.is_cloudflare_blocking(page_content):
                    cloudflare = True
                    sleep(1)
                else:
                    if cloudflare:
                        request_data = db.search(where('domain') == onlydomain)
                        if(len(request_data) > 0):
                            db.remove(where('domain') == onlydomain)
                        agent = await page.evaluate('navigator.userAgent')
                        headers = { 'user-agent': agent }
                        cookiesB = await browser.cookies.get_all()
                        cookies={}
                        for cookie in cookiesB:
                            if(cookie.name == 'cf_clearance'):
                                cookies = {'cf_clearance': cookie.value}
                        db.insert(RequestData(domain=onlydomain, headers=headers, cookies=cookies).as_dict())
                    content = base64.b64decode(fetch_content)
                    break
            browser.stop()
        uc.loop().run_until_complete(get_cloudflare_cookie())
        return content