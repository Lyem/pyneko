import base64
import tldextract
import nodriver as uc
from time import sleep
from bs4 import BeautifulSoup
from core.config.request_data import RequestData
from core.cloudflare.domain.request_entity import Request
from core.cloudflare.domain.bypass_repository import BypassRepository
from core.cloudflare.infra.nodriver.chrome import find_chrome_executable
from core.config.request_data import get_request, delete_request, insert_request, RequestData

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
    
    def is_cloudflare_bad_gatway(self, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string if soup.title else ""
        if "Bad gateway" in title:
            return True
        
        return False
    
    def is_cloudflare_attention(self, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string if soup.title else ""
        if "Attention Required! | Cloudflare" in title:
            return True
        
        return False
        
    def is_cloudflare_enable_cookies(self, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')

        alert = soup.select_one('div#cookie-alert')
        if alert:
            return True
        
        return False

    def bypass_cloudflare(self, url: str) -> Request:
        headers={}
        cookies={}
        async def get_cloudflare_cookie():
            nonlocal headers, cookies
            browser = await uc.start(
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
                browser_executable_path=None
            )
            page = await browser.get(url)
            request_data = get_request(onlydomain)
            if(request_data):
                re = request_data
                await page.evaluate(f'document.cookie = "cf_clearance={re.cookies['cf_clearance']}; path=/; max-age=3600; secure; samesite=strict";')
                await page.reload()
            while(True):
                page_content = await page.get_content()
                soup = BeautifulSoup(page_content, 'html.parser')
                head = soup.find('head')
                if self.is_cloudflare_blocking(page_content):
                    cloudflare = True
                    sleep(1)
                elif head and not head.contents:
                    content = None
                    break
                else:
                    if cloudflare:
                        request_data = get_request(onlydomain)
                        if(request_data):
                            delete_request(onlydomain)
                        agent = await page.evaluate('navigator.userAgent')
                        headers = { 'user-agent': agent }
                        cookiesB = await browser.cookies.get_all()
                        cookies={}
                        for cookie in cookiesB:
                            if(cookie.name == 'cf_clearance'):
                                cookies = {'cf_clearance': cookie.value}
                        insert_request(RequestData(domain=onlydomain, headers=headers, cookies=cookies))
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
                browser_executable_path=None,
                headless=background
            )
            page = await browser.get(domain)
            request_data = get_request(onlydomain)
            if(request_data):
                re = request_data
                if(re.cookies):
                    await page.evaluate(f'document.cookie = "cf_clearance={re.cookies['cf_clearance']}; path=/; max-age=3600; secure; samesite=strict";')
                    await page.reload()
                    cloudflare = False
            while(True):
                try:
                    page = await browser.get(domain)
                    page_content = await page.get_content()
                    soup = BeautifulSoup(page_content, 'html.parser')
                    head = soup.find('head')
                    if self.is_cloudflare_blocking(page_content):
                        cloudflare = True
                        sleep(1)
                    elif head and not head.contents:
                        content = None
                        break
                    else:
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
                        if cloudflare:
                            request_data = get_request(onlydomain)
                            if(request_data):
                                delete_request(onlydomain)
                            agent = await page.evaluate('navigator.userAgent')
                            headers = { 'user-agent': agent }
                            cookiesB = await browser.cookies.get_all()
                            cookies={}
                            for cookie in cookiesB:
                                if(cookie.name == 'cf_clearance'):
                                    cookies = {'cf_clearance': cookie.value}
                            insert_request(RequestData(domain=onlydomain, headers=headers, cookies=cookies))
                        content = base64.b64decode(fetch_content)
                        break
                except Exception as e:
                    print(e)
            browser.stop()
        uc.loop().run_until_complete(get_cloudflare_cookie())
        return content

    def bypass_cloudflare_no_capcha_post(self, domain: str, url: str, background = False) -> any:
        content={}
        async def get_cloudflare_cookie():
            nonlocal content
            cloudflare = False
            extract = tldextract.extract(domain)
            onlydomain = f"{extract.domain}.{extract.suffix}"
            browser = await uc.start(
                browser_executable_path=None,
                headless=background
            )
            page = await browser.get(domain)
            request_data = get_request(onlydomain)
            if(request_data):
                re = request_data
                if(re.cookies):
                    await page.evaluate(f'document.cookie = "cf_clearance={re.cookies['cf_clearance']}; path=/; max-age=3600; secure; samesite=strict";')
                    await page.reload()
                    cloudflare = False
            while(True):
                try:
                    page = await browser.get(domain)
                    page_content = await page.get_content()
                    soup = BeautifulSoup(page_content, 'html.parser')
                    head = soup.find('head')
                    if self.is_cloudflare_blocking(page_content):
                        cloudflare = True
                        sleep(1)
                    elif head and not head.contents:
                        content = None
                        break
                    else:
                        fetch_content = await page.evaluate(f'''
                            fetch("{url}", {{method: "POST"}})''' + '''.then(response => response.arrayBuffer()).then(buffer => {
                                let binary = '';
                                let bytes = new Uint8Array(buffer);
                                let len = bytes.byteLength;
                                for (let i = 0; i < len; i++) {
                                    binary += String.fromCharCode(bytes[i]);
                                }
                                return btoa(binary);
                            });
                        ''', await_promise=True)
                        if cloudflare:
                            request_data = get_request(onlydomain)
                            if(request_data):
                                delete_request(onlydomain)
                            agent = await page.evaluate('navigator.userAgent')
                            headers = { 'user-agent': agent }
                            cookiesB = await browser.cookies.get_all()
                            cookies={}
                            for cookie in cookiesB:
                                if(cookie.name == 'cf_clearance'):
                                    cookies = {'cf_clearance': cookie.value}
                            insert_request(RequestData(domain=onlydomain, headers=headers, cookies=cookies))
                        content = base64.b64decode(fetch_content)
                        break
                except Exception as e:
                    print(e)
            browser.stop()
        uc.loop().run_until_complete(get_cloudflare_cookie())
        return content