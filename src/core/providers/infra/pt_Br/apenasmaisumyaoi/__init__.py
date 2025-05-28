from core.providers.infra.template.wordpress_madara import WordPressMadara
from core.providers.domain.entities import Chapter, Pages
from core.__seedwork.infra.http import Http
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import nodriver as uc
import re

class ApenasMaisUmYaoiProvider(WordPressMadara):
    name = 'Apenas mais um yaoi'
    lang = 'pt-Br'
    domain = ['apenasmaisumyaoi.com']

    def __init__(self):
        self.url = 'https://apenasmaisumyaoi.com'

        self.path = ''
        
        self.query_mangas = 'div.post-title h3 a, div.post-title h5 a'
        self.query_chapters = 'li.wp-manga-chapter > a'
        self.query_chapters_title_bloat = None
        self.query_pages = 'div.page-break'
        self.query_title_for_uri = 'head meta[property="og:title"]'
        self.query_placeholder = '[id^="manga-chapters-holder"][data-id]'
    
    # def decrypt(self, domain: str, script: str, background = False) -> any:
    #     content=[]
    #     async def get_script_result():
    #         nonlocal content
    #         browser = await uc.start(
    #             browser_args=[
    #                 '--window-size=600,600', 
    #                 f'--app={domain}',
    #                 '--disable-extensions', 
    #                 '--disable-popup-blocking'
    #             ],
    #             browser_executable_path=None,
    #             headless=background
    #         )
    #         page = await browser.get(domain)
    #         cdn_cryptojs = "https://apenasmaisumyaoi.com/wp-content/plugins/wp-manga-chapter-images-protection/assets/js/crypto-js/crypto-js.js?ver=6.5.5"
    #         crypto = Http.get(cdn_cryptojs).data
    #         await page.evaluate(crypto)
    #         scripts = """
    #         const CryptoJSAesJson = {
    #             stringify: function (cipherParams) {
    #                 const jsonParams = { ct: cipherParams.ciphertext.toString(CryptoJS.enc.Base64) };
    #                 cipherParams.iv && (jsonParams.iv = cipherParams.iv.toString());
    #                 cipherParams.salt && (jsonParams.s = cipherParams.salt.toString());
    #                 return JSON.stringify(jsonParams);
    #             },
    #             parse: function (jsonString) {
    #                 const params = JSON.parse(jsonString);
    #                 const cipherParams = CryptoJS.lib.CipherParams.create({
    #                     ciphertext: CryptoJS.enc.Base64.parse(params.ct),
    #                 });
    #                 params.iv && (cipherParams.iv = CryptoJS.enc.Hex.parse(params.iv));
    #                 params.s && (cipherParams.salt = CryptoJS.enc.Hex.parse(params.s));
    #                 return cipherParams;
    #             },
    #         };

    #         const decryptData = function (encryptedData, password) {
    #             const decryptedData = JSON.parse(
    #                 CryptoJS.AES.decrypt(encryptedData, password, {
    #                     format: CryptoJSAesJson,
    #                 }).toString(CryptoJS.enc.Utf8)
    #             );
    #             const jsonData = JSON.parse(decryptedData);
    #             return jsonData;
    #         };
    #         """
    #         await page.evaluate(scripts)
    #         response = await page.evaluate(script)

    #         content = response
    #         browser.stop()
    #     uc.loop().run_until_complete(get_script_result())
    #     return content
    
    # def getPages(self, ch: Chapter) -> Pages:
    #     uri = urljoin(self.url, ch.id)
    #     uri = self._add_query_params(uri, {'style': 'list'})
    #     response = Http.get(uri)
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     script_tag = soup.find('script', {'id': 'chapter-protector-data'})

    #     script_content = script_tag.string

    #     regex = r"(\w+)\s*=\s*'([^']*)'"
    #     matches = re.findall(regex, script_content)

    #     variables = {match[0]: match[1] for match in matches}

    #     data = variables['chapter_data']
    #     password = variables['wpmangaprotectornonce'];

    #     script = f'''
    #         const data = '{data}';
    #         const password = "{password}";
    #         decryptData(data, password);
    #     '''

    #     list = self.decrypt('https://google.com', script, True)
    #     number = re.findall(r'\d+', str(ch.number))[0]
    #     return Pages(ch.id, number, ch.name, list)

