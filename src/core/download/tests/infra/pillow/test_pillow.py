import os
import shutil
from core.providers.domain.page_entity import Pages
from core.download.infra.pillow import PillowDownloadRepository

class TestUserRepositoryTinydb:
    
    def test_Pillow_Download(self):
        images = Pages('id', '20', 'solo leveling fake', ['https://cdn.nixmangas.com/mangas/o-comeco-depois-do-fim/175/0.webp', 'https://cdn.nixmangas.com/mangas/o-comeco-depois-do-fim/175/0.webp'])
        files = PillowDownloadRepository.download(images)
        
        assert files.number == '20'
        for file in files.files:
            assert os.path.exists(file)
        
        shutil.rmtree(os.path.join(os.getcwd(), 'mangas'))