from core.__seedwork.infra.http.contract.http import Http, Response
from core.cloudflare.application.use_cases import IsCloudflareBlockingUseCase, BypassCloudflareUseCase
from tinydb import TinyDB, where, Query
from platformdirs import user_data_path
from httpx import get, post
import tldextract
from core.config.request_data import RequestData
from os import makedirs
from time import sleep

data_path = user_data_path('pyneko')
db_path = data_path / 'request.json'
makedirs(data_path, exist_ok=True)
db = TinyDB(db_path)

class HttpxService(Http):
    
    @staticmethod
    def get(url: str, params=None, headers=None, cookies=None, **kwargs) -> Response:
        status = 0
        count = 0
        extract = tldextract.extract(url)
        domain = f"{extract.domain}.{extract.suffix}"

        while(status not in range(200, 299) and count <= 10):
            count += 1

            request_data = db.search(where('domain') == domain)

            if(len(request_data) > 0):
                re = RequestData.from_dict(request_data[0])
                if headers != None: headers = headers | re.headers
                else: headers = re.headers
                if cookies != None: cookies = cookies | re.cookies
                else: cookies = re.cookies
        
            response = get(url, params=params, headers=headers, cookies=cookies, timeout=None, **kwargs)
            status = response.status_code
            # print(status)
            # print(url)

            if response.status_code == 403:
                if IsCloudflareBlockingUseCase().execute(response.text):
                    request_data = db.search(where('domain') == domain)
                    if(len(request_data) > 0):
                        db.remove(where('domain') == domain)
                    data = BypassCloudflareUseCase().execute(f'https://{domain}')
                    db.insert(RequestData(domain=domain, headers=data.user_agent, cookies=data.cloudflare_cookie_value).as_dict())

            elif status not in range(200, 299) and not 403 and not 429:
                sleep(1)
            elif status == 429:
                sleep(60)
            elif status == 301 and 'Location' in response.headers:
                new_url = f'https://{domain}{response.headers['Location']}'
                response = get(new_url, params=params, headers=headers, cookies=cookies, timeout=None, **kwargs)
                status = response.status_code
            if status in range(200, 299):
                return Response(response.status_code, response.text, response.content, url)

        raise Exception(f"Failed to fetch the URL STATUS: {status}")

    
    @staticmethod
    def post(url, data=None, json=None, headers=None, cookies=None, **kwargs) -> Response:
        status = 0
        count = 0
        extract = tldextract.extract(url)
        domain = f"{extract.domain}.{extract.suffix}"

        while(status not in range(200, 299) and count <= 10):
            count += 1

            request_data = db.search(where('domain') == domain)

            if(len(request_data) > 0):
                re = RequestData.from_dict(request_data[0])
                if headers != None: headers = headers | re.headers
                else: headers = re.headers
                if cookies != None: cookies = cookies | re.cookies
                else: cookies = re.cookies

            response = post(url, data=data, json=json, headers=headers, cookies=cookies, timeout=None, **kwargs)
            status = response.status_code

            if response.status_code == 403:
                if IsCloudflareBlockingUseCase().execute(response.text):
                    data = BypassCloudflareUseCase().execute(f'https://{domain}')
                    response = post(url, data=data, json=json, headers=headers, cookies=cookies, **kwargs)
                    if IsCloudflareBlockingUseCase().execute(response.text):
                        data = BypassCloudflareUseCase().execute(url)
                    db.insert(RequestData(domain=domain, headers=data.user_agent, cookies=data.cloudflare_cookie_value).as_dict())
            elif status not in range(200, 299) and not 403 and not 429:
                sleep(1)
            elif status == 429:
                sleep(60)
            else:
                return Response(response.status_code, response.text, response.content, url)

        raise Exception("Failed to fetch the URL")