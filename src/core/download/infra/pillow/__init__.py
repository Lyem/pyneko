import re
import os
import math
from PIL import Image
from io import BytesIO
from core.config.img_conf import get_config
from core.__seedwork.infra.http import Http
from core.providers.domain.page_entity import Pages
from core.download.domain.dowload_entity import Chapter
from core.download.domain.dowload_repository import DownloadRepository
from core.__seedwork.infra.utils.sanitize_folder import sanitize_folder_name
Image.MAX_IMAGE_PIXELS = 933120000

class PillowDownloadRepository(DownloadRepository):

    def download(self, pages: Pages, fn=None, headers=None, cookies=None, timeout=None) -> Chapter:
        title = sanitize_folder_name(pages.name)
        config = get_config()
        img_path = config.save
        path = os.path.join(img_path, str(title), str(sanitize_folder_name(pages.number)))
        os.makedirs(path, exist_ok=True)
        img_format = config.img

        page_number = 1
        files = []
        for i, page in enumerate(pages.pages):
            response = Http.get(page, headers=headers, cookies=cookies, timeout=timeout)
            try:
                img = Image.open(BytesIO(response.content))
                icc = img.info.get('icc_profile')
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                file = os.path.join(path, f"%03d{img_format}" % page_number)
                img.save(file, quality=100, dpi=(72, 72), icc_profile=icc)
                files.append(file)
            except Exception as e:
                print(f"<stroke style='color:green;'>[Downloading]:</stroke> <span style='color:red;'>Error</stroke> {e}")

            if fn != None:
                fn(math.ceil(i * 100)/len(pages.pages))
            page_number += 1

        if fn != None:
            fn(math.ceil(len(pages.pages) * 100)/len(pages.pages))

        return Chapter(pages.number, files)