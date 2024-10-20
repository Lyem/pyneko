import os
import pillow_avif
from PIL import Image as pil
pil.Image.MAX_IMAGE_PIXELS = 933120000

class ImageHandler:
    def load(self, files: list[str]) -> list[pil.Image]:
        img_objs = []
        for imgPath in files:
            image = pil.open(imgPath)
            img_objs.append(image)
        return img_objs

    def save(
        self,
        output_path: str,
        img_obj: pil.Image,
        img_iteration: 1,
        img_format: str = '.jpg',
        quality=100,
    ) -> str:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        img_file_name = str(f'{img_iteration:02}') + img_format
        img_obj.save(
            output_path + '/' + img_file_name,
            quality=quality,
        )
        img_obj.close()
        return img_file_name