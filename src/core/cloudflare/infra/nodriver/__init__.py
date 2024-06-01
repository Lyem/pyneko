import nodriver as uc
from time import sleep
from bs4 import BeautifulSoup
from core.cloudflare.domain.request_entity import Request
from core.cloudflare.domain.bypass_repository import BypassRepository

class Cloudflare(BypassRepository):
    def is_cloudflare_blocking(self, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string if soup.title else ""
        if "Just a moment..." in title:
            return True
        
        if "Um momento…" in title:
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
                ],
                browser_executable_path=None
            )
            page = await browser.get(url)
            agent = await page.evaluate('navigator.userAgent')
            headers = { 'user-agent': agent }
            while(True):
                page_content = await page.evaluate('document.documentElement.outerHTML')
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