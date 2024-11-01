from pathlib import Path
from tinydb import TinyDB
from os import makedirs, getcwd, path
from platformdirs import user_config_dir
from dataclasses import dataclass, asdict

config_path = user_config_dir('pyneko')
db_path = Path(config_path) / 'img3.json'
makedirs(config_path, exist_ok=True)
db = TinyDB(db_path)

@dataclass
class Config:
    img: str
    save: str = path.join(getcwd(), 'mangas')
    group_format: str = '.pdf'
    group: bool = False
    slice: bool = False
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
    data = Config(img='.jpg', save=path.join(getcwd(), 'mangas'), slice=False, detection_type='pixel', custom_width=0, split_height=500, detection_senstivity=90, ignorable_pixels=5, scan_line_step=5, automatic_width=False, group_format='.pdf', group=False)
    db.insert(data.as_dict())
    return data

def get_config() -> Config:
    data = db.all()
    if len(data) == 0:
        return init()
    return Config.from_dict(data[0])

def update_img(img: str) -> None:
    config = get_config()
    db.update(Config(img=img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_save(save: str) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_slice(slice: bool) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_detection_type(detection_type: str | None) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_custom_width(custom_width: int | None) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_split_height(split_height: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_detection_senstivity(detection_senstivity: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_ignorable_pixels(ignorable_pixels: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_scan_line_step(scan_line_step: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=scan_line_step, automatic_width=config.automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_automatic_width(automatic_width: bool) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=automatic_width, group_format=config.group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_group_format(group_format: str) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=config.automatic_width, group_format=group_format, group=config.group).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_group(group: int) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=config.save, slice=config.slice, detection_type=config.detection_type, custom_width=config.custom_width, split_height=config.split_height, detection_senstivity=config.detection_senstivity, ignorable_pixels=config.ignorable_pixels, scan_line_step=config.scan_line_step, automatic_width=config.automatic_width, group_format=config.group_format, group=group).as_dict(),  doc_ids=[db.all()[0].doc_id])
