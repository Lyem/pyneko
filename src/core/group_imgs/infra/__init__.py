import zipfile
import pillow_avif
from PIL import Image
from pathlib import Path
from core.config.img_conf import get_config
from core.download.domain.dowload_entity import Chapter
Image.MAX_IMAGE_PIXELS = 933120000

class GroupImages():
    def run(self, ch: Chapter, fn=None):
        conf = get_config()
        if conf.group_format == '.pdf':
                path = Path.joinpath(Path(ch.files[0]).parent.parent,f'{ch.number}.pdf')
                first = Image.open(ch.files[0]).convert('RGB')
                all_imgs = [Image.open(img).convert('RGB') for img in ch.files[1:]]
                first.save(path, save_all=True, append_images=all_imgs)
        else:
            path = Path.joinpath(Path(ch.files[0]).parent.parent,f'{ch.number}.zip')
            with zipfile.ZipFile(path, 'w') as zipf:
                for img in ch.files:
                    zipf.write(img)