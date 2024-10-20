import os
import math
import pillow_avif
from PIL import Image
from pathlib import Path
Image.MAX_IMAGE_PIXELS = 933120000
from waifu2x_ncnn_py import Waifu2x
from core.config.img_conf import get_config
from core.download.domain.dowload_entity import Chapter

class UpscaleRepository():
    def upscale(self, ch: Chapter, fn=None) -> Chapter:
        conf = get_config()
        files = []
        waifu2x = Waifu2x(gpuid=conf.waifu2x_gpuid, tta_mode=False, num_threads=conf.waifu2x_threads, noise=conf.waifu2x_noise, scale=conf.waifu2x_scale, tilesize=conf.waifu2x_tilesize, model=conf.waifu2x_model)
        for i, file in enumerate(ch.files):
            folder = Path.joinpath(Path(ch.files[0]).parent.parent, f'{ch.number} [scaled]')
            os.makedirs(folder, exist_ok=True)
            path = Path.joinpath(folder, f'{i}{conf.img}')
            with Image.open(file) as image:
                image = waifu2x.process_pil(image)
                image.save(path, quality=95)
                files.append(path)
            
            if fn != None:
                fn(math.ceil(i * 100)/len(ch.files))

        if fn != None:
            fn(math.ceil(len(ch.files) * 100)/len(ch.files))

        return Chapter(ch.number, files)
        