from pathlib import Path
from tinydb import TinyDB
from os import makedirs, remove
from PyQt6.QtCore import QLocale
from platformdirs import user_config_dir
from dataclasses import dataclass, asdict

config_path = user_config_dir('pyneko')
db_path = Path(config_path) / 'ui.json'
makedirs(config_path, exist_ok=True)
db = TinyDB(db_path)

@dataclass
class Config:
    lang: str
    progress: bool = False
    max_download: int = 3
    log: bool = False

    def as_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return Config(**data)

def get_config() -> Config | None:
    data = db.all()
    if len(data) == 0:
        return None
    return Config.from_dict(data[0])

def init(lang: str) -> None:
    db.insert(Config(lang=lang, progress=False, max_download=3, log=False).as_dict())

def update_max_download(max_download: int):
    data = get_config()
    db.update(Config(lang=data.lang, progress=data.progress, max_download=max_download, log=data.log).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_progress(progress: bool):
    data = get_config()
    db.update(Config(lang=data.lang, progress=progress, max_download=data.max_download, log=data.log).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_log(log: bool):
    data = get_config()
    db.update(Config(lang=data.lang, progress=data.progress, max_download=data.max_download, log=log).as_dict(),  doc_ids=[db.all()[0].doc_id])

def update_lang(lang: str) -> None:
    data = get_config()
    
    if not data:
        init(lang=lang)
        return None

    db.update(Config(lang=lang, progress=data.progress, max_download=data.max_download, log=data.log).as_dict(),  doc_ids=[db.all()[0].doc_id])

