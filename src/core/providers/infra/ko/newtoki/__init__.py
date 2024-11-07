import re
import tldextract
import nodriver as uc
from time import sleep
from typing import List
from bs4 import BeautifulSoup
from tldextract import extract
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.download.application.use_cases import DownloadUseCase
from core.providers.domain.entities import Chapter, Pages, Manga
from core.cloudflare.application.use_cases import IsCloudflareBlockingUseCase
from core.config.request_data import get_request, delete_request, insert_request, RequestData

class NewTokiProvider(Base):
    name = 'New Toki'
    lang = 'ko'
    domain = [re.compile(r'^newtoki\d*\.com$')]
    
    def getManga(self, link: str) -> Manga:
        content={}
        response = Http.get(link)
        if self._is_capcha(response.content):
            while(True):
                content = self.bypass_capcha(link)
                if content:
                    break
        else:
            content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.select_one('div.col-sm-8')
        title = title.select_one('div.view-content')
        title = title.select_one('span')
        title = title.select_one('b').get_text().strip()
        return Manga(link, title)

    def getChapters(self, id: str) -> List[Chapter]:
        content={}
        response = Http.get(id)
        if self._is_capcha(response.content):
            while(True):
                content = self.bypass_capcha(id)
                if content:
                    break
        else:
            content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.select_one('div.col-sm-8')
        title = title.select_one('div.view-content')
        title = title.select_one('span')
        title = title.select_one('b').get_text().strip()
        list_body = soup.select_one('ul.list-body')
        caps = list_body.select('li')
        list = []
        for cap in caps:
            a = cap.select_one('div.wr-subject')
            a = a.select_one('a.item-subject')
            for span in a.find_all('span'):
                span.extract()
            list.append(Chapter(id=a.get('href'), number=a.get_text().strip().replace(f"{title}", ""), name=title))
        return list
    
    def _is_capcha(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        meta_tags = soup.find_all('meta', content=True)
        found = any('bbs/captcha.php' in tag['content'] for tag in meta_tags)
        if found:
            return True
        return False
    
    def bypass_capcha(self, url: str) -> str:
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
            scroll = True
            request_data = get_request(onlydomain)
            if(request_data):
                re = request_data
                await page.evaluate(f'document.cookie = "cf_clearance={re.cookies['cf_clearance']}; path=/; max-age=3600; secure; samesite=strict";')
                await page.reload()
            while(True):
                page_content = await page.get_content()
                soup = BeautifulSoup(page_content, 'html.parser')
                head = soup.find('head')
                if IsCloudflareBlockingUseCase().execute(page_content):
                    cloudflare = True
                    sleep(1)
                if self._is_capcha(page_content):
                    sleep(2)
                    if scroll:
                        scroll = False
                        await page.evaluate('''
                            const formBox = document.querySelector('.form-box');
                            if (formBox) {
                                formBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            } else {
                                console.log("Elemento com a classe 'form-box' não encontrado.");
                            }
                        ''', await_promise=True)
                elif head and not head.contents:
                    content = None
                    break
                else:
                    sleep(5)
                    page_content = await page.get_content()
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

    def getPages(self, ch: Chapter) -> Pages:
        list = []
        content={}
        while(True):
            content = self.bypass_capcha(ch.id)
            if content:
                break
        try:
            soup = BeautifulSoup(content, 'html.parser')
            div = soup.select('div.view-padding')[1]
            imgs = div.select('img')
            pattern = r'https://img[^\s"]+'
            imgs = re.findall(pattern, str(imgs))
            unique_urls = []
            for img in imgs:
                if img not in unique_urls:
                    unique_urls.append(img)
            for img in unique_urls:
                list.append(img)
        except Exception as e:
            print(e)
        return Pages(ch.id, ch.number, ch.name, list)

    def download(self, pages: Pages, fn: any, headers=None, cookies=None):
        extract_info = extract(pages.id)
        domain = f"{extract_info.domain}.{extract_info.suffix}"
        headers = {'referer': f'https://{domain}'}
        return DownloadUseCase().execute(pages=pages, fn=fn, headers=headers, cookies=cookies)

