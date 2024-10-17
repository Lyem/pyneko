from os import makedirs
from tinydb import TinyDB
from pathlib import Path
from platformdirs import user_config_dir
from dataclasses import dataclass, asdict

config_path = user_config_dir('pyneko')
db_path = Path(config_path) / 'ui.json'
makedirs(config_path, exist_ok=True)
db = TinyDB(db_path)

@dataclass
class Config:
    lang: str

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
    db.insert(Config(lang=lang).as_dict())

def update_lang(lang: str) -> None:
    data = get_config()
    
    if not data:
        init(lang=lang)
        return None

    db.update(Config(lang=lang).as_dict(),  doc_ids=[db.all()[0].doc_id])

