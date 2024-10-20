from pathlib import Path
from tinydb import TinyDB
from os import makedirs, getcwd, path
from platformdirs import user_config_dir
from dataclasses import dataclass, asdict

config_path = user_config_dir('pyneko')
db_path = Path(config_path) / 'img.json'
makedirs(config_path, exist_ok=True)
db = TinyDB(db_path)

@dataclass
class Config:
    img: str
    save: str = path.join(getcwd(), 'mangas')
    group_format: str = '.pdf'
    group: bool = False
    slice: bool = False
    waifu2x: bool = False
    waifu2x_model: str = 'models-cunet'
    waifu2x_gpuid: int = -1,
    waifu2x_threads: int = 1,
    waifu2x_noise: int = 0,
    waifu2x_scale: int = 2,
    waifu2x_tilesize: int = 0
    detection_type: str | None = 'pixel'
    custom_width: int = 0
    automatic_width: bool = False
    split_height: int = 500
    detection_senstivity: int = 90
    ignorable_pixels: int = 5
    scan_line_step: int = 5

    def as_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return Config(**data)

def init() -> Config:
    data = Config(img='.jpg', save=path.join(getcwd(), 'mangas'), slice=False, waifu2x=False, detection_type='pixel', custom_width=0, split_height=500, detection_senstivity=90, ignorable_pixels=5, scan_line_step=5, waifu2x_model='models-cunet', waifu2x_gpuid=-1, waifu2x_threads=1, waifu2x_noise=0, waifu2x_scale=2, waifu2x_tilesize=0, automatic_width=False, group_format='.pdf', group=False)
    db.insert(data.as_dict())
    return data

def get_config() -> Config:
    data = db.all()
    if len(data) == 0:
        return init()
    return Config.from_dict(data[0])

def update_img(img: str) -> None:
    config = get_config()
    db.update(Config(img=img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_save(save: str) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_slice(slice: bool) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_detection_type(detection_type: str | None) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_custom_width(custom_width: int | None) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_split_height(split_height: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_detection_senstivity(detection_senstivity: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_ignorable_pixels(ignorable_pixels: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_scan_line_step(scan_line_step: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_automatic_width(automatic_width: bool) -> None:
    config = get_config()
    print(automatic_width)
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])
    teste = get_config()
    print(teste.automatic_width)

def update_waifu2x(waifu2x: bool) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_waifu2x_model(waifu2x_model: str) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_waifu2x_gpuid(waifu2x_gpuid: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_waifu2x_threads(waifu2x_threads: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_waifu2x_noise(waifu2x_noise: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_waifu2x_scale(waifu2x_scale: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_waifu2x_tilesize(waifu2x_tilesize: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_group_format(group_format: str) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_group(group: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, waifu2x=config.waifu2x, waifu2x_model=config.waifu2x_model, waifu2x_gpuid=config.waifu2x_gpuid, waifu2x_threads=config.waifu2x_threads, waifu2x_noise=config.waifu2x_noise, waifu2x_scale=config.waifu2x_scale, waifu2x_tilesize=config.waifu2x_tilesize, automatic_width=config.automatic_width, group_format=config.group_format, group=group).as_dict(),  doc_ids=[db.all()[0].doc_id])
