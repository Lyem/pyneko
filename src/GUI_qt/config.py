import sqlite3
from os import makedirs
from pathlib import Path
from platformdirs import user_config_dir
from dataclasses import dataclass, asdict

config_path = user_config_dir('pyneko')
db_path = Path(config_path) / 'ui.db'
makedirs(config_path, exist_ok=True)

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
        return cls(**data)

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS config (
                        lang TEXT,
                        progress INTEGER,
                        max_download INTEGER,
                        log INTEGER
                      )''')
    conn.commit()
    conn.close()

def init(lang: str) -> None:
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO config VALUES (?, ?, ?, ?)',
                   (lang, 0, 3, 0))
    conn.commit()
    conn.close()

def get_config() -> Config | None:
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM config LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return Config(lang=row[0], progress=bool(row[1]), max_download=row[2], log=bool(row[3]))

def update_config_field(field: str, value):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'UPDATE config SET {field} = ? WHERE rowid = 1', (int(value) if isinstance(value, bool) else value,))
    conn.commit()
    conn.close()

def update_max_download(max_download: int):
    update_config_field('max_download', max_download)

def update_progress(progress: bool):
    update_config_field('progress', progress)

def update_log(log: bool):
    update_config_field('log', log)

def update_lang(lang: str) -> None:
    data = get_config()
    if not data:
        init(lang=lang)
        return None
    update_config_field('lang', lang)
