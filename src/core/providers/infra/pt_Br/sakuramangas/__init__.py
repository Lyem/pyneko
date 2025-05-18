import re
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga

# Construído com base no código disponível em https://github.com/etoshy/Sakura-Mangas-Downloader por etoshy

class SakuraMangasProvider(Base):
    name = 'Sakura Mangas'
    lang = 'pt_Br'
    domain = ['sakuramangas.org']

    def __init__(self) -> None:
        self.base_url = 'https://sakuramangas.org'

    def extract_manga_info(self, url):
        try:
            response = Http.get(url)
            if response.status == 200:
                manga_id_match = re.search(r'<meta\s+manga-id="(\d+)">', response.text())
                token_match = re.search(r'<meta\s+token="([^"]+)">', response.text())
                
                if manga_id_match and token_match:
                    manga_id = manga_id_match.group(1)
                    token = token_match.group(1)
                    return {"manga_id": manga_id, "token": token}
                else:
                    parsed_url = urlparse(url)
                    path_parts = parsed_url.path.strip('/').split('/')
                    if len(path_parts) >= 2:
                        obra_name = path_parts[-2]
                        print(f"Não encontrou tags de metadados, mas encontrou nome da obra: {obra_name}")
                    
                    print("Não foi possível extrair manga_id e token da página")
                    return None
            else:
                print(f"Falha ao acessar URL: {response.status}")
                return None
        except Exception as e:
            print(f"Erro ao extrair informações do mangá: {e}")
            return None
    
    def getManga(self, link: str) -> Manga:
        infos = self.extract_manga_info(link)
        if infos == None:
            print("Não foi possível extrair informações do mangá.")
            return None
        url = f'{self.base_url}/dist/sakura/models/manga/manga_info.php'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {
            'manga_id': infos['manga_id'],
            'token': infos['token'],
            'dataType': 'json'
        }
        
        try:
            response = Http.post(url, headers=headers, data=data)
            if response.status == 200:
                return Manga(f'{infos["manga_id"]}|{infos["token"]}|{response.json().get("ultimo_capitulo", 1)}|{response.json().get("titulo", "Desconhecido")}', response.json().get("titulo", "Desconhecido"))
            else:
                print(f"Falha ao obter detalhes do mangá: {response.status}")
                return None
        except Exception as e:
            print(f"Erro ao obter detalhes do mangá: {e}")
            return None

    def getChapters(self, id: str) -> List[Chapter]:
        datas = id.split('|')
        title=datas[3]
        last_chapter = int(datas[2])
        manga_id=datas[0]
        token=datas[1]
        url = f'{self.base_url}/dist/sakura/models/manga/manga_capitulos.php'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        all_chapters_html = ""
        all_chapters_data = []
        
        # Calcula quantas requisições precisamos fazer
        limit = 90
        requests_needed = (last_chapter // limit) + 1
        
        for i in range(requests_needed):
            offset = i * limit
            data = {
                'manga_id': manga_id,
                'token': token,
                'offset': offset,
                'order': 'desc',
                'limit': limit
            }
            
            try:
                response = Http.post(url, headers=headers, data=data)
                if response.status == 200:
                    chapters_html = response.text()
                    
                    # Analisa o HTML para extrair informações dos capítulos
                    soup = BeautifulSoup(chapters_html, 'html.parser')
                    chapter_items = soup.find_all('div', class_='capitulo-item')
                    
                    for chapter in chapter_items:
                        try:
                            chapter_num_span = chapter.find('span', class_='num-capitulo')
                            if not chapter_num_span:
                                continue
                                
                            chapter_num = chapter_num_span.get('data-chapter', '')
                            chapter_link_elem = chapter_num_span.find('a')
                            chapter_link = chapter_link_elem['href'] if chapter_link_elem else ''
                            chapter_title = chapter.find('span', class_='cap-titulo').text.strip() if chapter.find('span', class_='cap-titulo') else ''
                            scan_name = chapter.find('span', class_='scan-nome').text.strip() if chapter.find('span', class_='scan-nome') else ''
                            
                            all_chapters_data.append(Chapter(chapter_link, chapter_num, title))
                        except Exception as e:
                            print(f"Erro ao analisar capítulo: {e}")
                            continue
                    
                    # Se recebemos menos itens que o limite, podemos parar
                    if len(chapter_items) < limit:
                        break
                        
                else:
                    print(f"Falha ao obter capítulos no offset {offset}: {response.status}")
                    break
            except Exception as e:
                print(f"Erro ao obter capítulos do mangá: {e}")
                break
    
        return all_chapters_data

    def extract_meta_from_url(self, url):
        try:
            # Tenta buscar o conteúdo da página primeiro
            response = Http.get(url)
            if response.status != 200:
                print(f"Falha ao acessar URL: {url}")
                return None, None
                
            content = response.text()
            
            # Extrai chapter_id e token usando regex
            chapter_id_match = re.search(r'<meta chapter-id="(\d+)">', content)
            token_match = re.search(r'<meta token="([^"]+)">', content)
            
            if chapter_id_match and token_match:
                chapter_id = chapter_id_match.group(1)
                token = token_match.group(1)
                return chapter_id, token
            else:
                print("Não foi possível encontrar chapter_id e token no conteúdo da página")
                return None, None
                
        except Exception as e:
            print(f"Erro ao acessar URL: {e}")
            return None, None

    def getPages(self, ch: Chapter) -> Pages:
        chapter_id, token = self.extract_meta_from_url(ch.id)
        url = f'{self.base_url}/dist/sakura/models/capitulo/capitulos_read.php'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = f'chapter_id={chapter_id}&token={token}'
        
        try:
            response = Http.post(url, headers=headers, data=data)
            if response.status != 200:
                print(f"Falha ao obter páginas do capítulo: Código de status {response.status}")
                return None
            pages_data = [self.base_url + path if path.startswith('/') else self.base_url + '/' + path for path in response.json().get('imageUrls', [])]
            return Pages(chapter_id, ch.number, ch.name, pages_data)
        except Exception as e:
            print(f"Erro ao obter páginas do capítulo: {e}")
            return None

