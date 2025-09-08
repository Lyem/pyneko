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
    external_provider: bool = False
    external_provider_path: str | None = None

    def as_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

def add_field_if_not_exists(field_name: str, field_type: str = 'TEXT', default_value: str = None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(config)")
    fields = [column[1] for column in cursor.fetchall()]
    
    if field_name not in fields:
        cursor.execute(f"ALTER TABLE config ADD COLUMN {field_name} {field_type}")
        if default_value is not None:
            cursor.execute(f"UPDATE config SET {field_name} = ? WHERE {field_name} IS NULL", (default_value,))
        conn.commit()
    conn.close()

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

    add_field_if_not_exists('external_provider_path')
    add_field_if_not_exists('external_provider', 'INTEGER', 0)

def init(lang: str) -> None:
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO config VALUES (?, ?, ?, ?, ?, ?)',
                   (lang, 0, 3, 0, None, 0))
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
    return Config(lang=row[0], progress=bool(row[1]), max_download=row[2], log=bool(row[3]), external_provider_path=row[4], external_provider=row[5])

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

def update_external_path(path: str):
    update_config_field('external_provider_path', path)

def update_external(external: bool):
    update_config_field('external_provider', external)
