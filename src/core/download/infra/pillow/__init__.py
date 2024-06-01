import os
import math
from PIL import Image
from io import BytesIO
from core.__seedwork.infra.http import Http
from core.providers.domain.page_entity import Pages
from core.download.domain.dowload_entity import Chapter
from core.download.domain.dowload_repository import DownloadRepository
Image.MAX_IMAGE_PIXELS = 933120000


class PillowDownloadRepository(DownloadRepository):

    def download(pages: Pages, fn=None, headers=None, cookies=None) -> Chapter:
        path = os.path.join(os.getcwd(), 'mangas',
                            f'{pages.name}', f'{pages.number}')
        os.makedirs(path, exist_ok=True)

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
                file = os.path.join(path, f"%03d.webp" % page_number)
                files.append(file)
                img.save(file, quality=80, dpi=(72, 72), icc_profile=icc)
            except:
                if response.status == 200:
                    file = os.path.join(path, f"%03d.webp" % page_number)
                    files.append(file)
                    with open(file, 'wb') as archive:
                        archive.write(response.content)
            if fn != None:
                fn(math.ceil(i * 100)/len(pages.pages))
            page_number += 1

        if fn != None:
            fn(math.ceil(len(pages.pages) * 100)/len(pages.pages))

        return Chapter(pages.number, files)
