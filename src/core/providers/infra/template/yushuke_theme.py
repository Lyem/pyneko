from typing import List
from bs4 import BeautifulSoup
from core.__seedwork.infra.http import Http
from core.providers.infra.template.base import Base
from core.providers.domain.entities import Chapter, Pages, Manga
import json

class YushukeTheme(Base):
    def __init__(self) -> None:
        self.url = None
        self.chapters_api = f'{self.url}/ajax/lzmvke.php?'
        
        self.title = 'div.manga-title-row h1'
        self.manga_id_selector = "button#CarregarCapitulos"
        self.chapter_item_selector = 'a.chapter-item'
        self.chapter_number_selector = 'span.capitulo-numero'
        self.chapter_views_selector = 'span.chapter-views'
        self.pages_selector = "div.select-nav + * picture"
        self.id_manga = 'data-page'
        self.image_selector = "img"

    def getManga(self, link: str) -> Manga:
        response = Http.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one('div.manga-title-row h1')

        return Manga(link, title.get_text(strip=True))

    def getChapters(self, id: str) -> List[Chapter]:
        response = Http.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one(self.title)
        chapter_list = []
        
        id_manga = soup.select_one(self.manga_id_selector)
        if not id_manga:
            # Fallback: Extract chapters directly from the page
            get_chapters = soup.select(self.chapter_item_selector)
            
            for ch in get_chapters:
                number_element = ch.select_one(self.chapter_number_selector)
                if number_element:
                    views_span = number_element.select_one(self.chapter_views_selector)
                    if views_span:
                        views_span.decompose()
                    
                    chapter_text = number_element.get_text(strip=True)
                    chapter_number = ' '.join(chapter_text.split()[:2])
                    
                    chapter_url = ch.get('href')
                    if not chapter_url.startswith('http'):
                        chapter_url = f'{self.url}{chapter_url}'
                    else:
                        chapter_url = ch.get('href')
                        
                    chapter_list.append(Chapter(
                        chapter_url,
                        chapter_number,
                        title.get_text(strip=True)
                    ))
            
            return chapter_list
        
        # Continue with API method if the button is found
        manga_id = id_manga.get(self.id_manga)
        current_page = 1
        
        while True:
            api_url = f'{self.chapters_api}manga_id={manga_id}&page={current_page}&order=DESC'
            response = Http.get(api_url)
            
            try:
                data = json.loads(response.content)
                # if not data.get('chapters') or data.get('remaining', 0) == 0:
                #     break
                chapters_html = BeautifulSoup(data['chapters'], 'html.parser')
                get_chapters = chapters_html.select(self.chapter_item_selector)
                
                if not get_chapters:
                    break
                    
                for ch in get_chapters:
                    number_element = ch.select_one(self.chapter_number_selector)
                    if number_element:
                        views_span = number_element.select_one(self.chapter_views_selector)
                        if views_span:
                            views_span.decompose()
                        
                        chapter_text = number_element.get_text(strip=True)
                        
                        chapter_number = ' '.join(chapter_text.split()[:2])
                        
                        chapter_url = ch.get('href')
                        if not chapter_url.startswith('http'):
                            chapter_url = f'{self.url}{chapter_url}'
                        else:
                            chapter_url = ch.get('href')
                            
                        chapter_list.append(Chapter(
                            chapter_url,
                            chapter_number,
                            title.get_text(strip=True)
                        ))
                
                current_page += 1
                
            except json.JSONDecodeError:
                break
                
        return chapter_list

    def getPages(self, ch: Chapter) -> Pages:
        response = Http.get(ch.id)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        images = []
        picture_elements = soup.select(self.pages_selector)
        
        for index, picture_element in enumerate(picture_elements):
            img_element = picture_element.select_one(self.image_selector)
            if img_element and img_element.get('src'):
                image_url = img_element.get('src')
                if image_url.strip():
                    images.append(f"{self.url}{image_url}")
        
        return Pages(ch.id, ch.number, ch.name, images)

