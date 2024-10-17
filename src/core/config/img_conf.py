from pathlib import Path
from tinydb import TinyDB
from os import makedirs, getcwd, path
from platformdirs import user_config_dir
from dataclasses import dataclass, asdict

config_path = user_config_dir('pyneko')
db_path = Path(config_path) / 'img_conf.json'
makedirs(config_path, exist_ok=True)
db = TinyDB(db_path)

@dataclass
class Config:
    img: str
    save: str

    def as_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return Config(**data)

def init() -> Config:
    data = Config(img='.jpg', save=path.join(getcwd(), 'mangas'))
    db.insert(data.as_dict())
    return data

def get_config() -> Config:
    data = db.all()
    if len(data) == 0:
        return init()
    return Config.from_dict(data[0])

def update_img(img: str) -> None:
    config = get_config()
    db.update(Config(img=img, save=config.save).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_save(save: str) -> None:
    config = get_config()
    db.update(Config(img=config.img, save=save).as_dict(),  doc_ids=[db.all()[0].doc_id])

