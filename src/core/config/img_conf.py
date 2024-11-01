import sqlite3
from os import makedirs, getcwd, path
from platformdirs import user_config_dir
from dataclasses import dataclass, asdict
from pathlib import Path

config_path = user_config_dir('pyneko')
db_path = Path(config_path) / 'config.db'
makedirs(config_path, exist_ok=True)

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
    detection_sensitivity: int = 90
    ignorable_pixels: int = 5
    scan_line_step: int = 5
    slice_replace_original_files: bool = False
    group_replace_original_files: bool = False

    def as_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

import sqlite3

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
                        img TEXT,
                        save TEXT,
                        group_format TEXT,
                        group_flag INTEGER,
                        slice INTEGER,
                        detection_type TEXT,
                        custom_width INTEGER,
                        automatic_width INTEGER,
                        split_height INTEGER,
                        detection_sensitivity INTEGER,
                        ignorable_pixels INTEGER,
                        scan_line_step INTEGER
                      )''')
    conn.commit()
    conn.close()

    add_field_if_not_exists('slice_replace_original_files', 'INTEGER', 0)
    add_field_if_not_exists('group_replace_original_files', 'INTEGER', 0)

def init() -> Config:
    init_db()
    config = Config(img='.jpg')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO config VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (config.img, config.save, config.group_format, int(config.group), int(config.slice),
                    config.detection_type, config.custom_width, int(config.automatic_width),
                    config.split_height, config.detection_sensitivity, config.ignorable_pixels, config.scan_line_step, 
                    int(config.slice_replace_original_files), int(config.group_replace_original_files)))
    conn.commit()
    conn.close()
    return config

def get_config() -> Config:
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM config LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return init()
    return Config(*row)

def update_config_field(field: str, value):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'UPDATE config SET {field} = ? WHERE rowid = 1', (value,))
    conn.commit()
    conn.close()

def update_img(img: str) -> None:
    update_config_field('img', img)

def update_save(save: str) -> None:
    update_config_field('save', save)

def update_slice(slice: bool) -> None:
    update_config_field('slice', int(slice))

def update_detection_type(detection_type: str | None) -> None:
    update_config_field('detection_type', detection_type)

def update_custom_width(custom_width: int) -> None:
    update_config_field('custom_width', custom_width)

def update_split_height(split_height: int) -> None:
    update_config_field('split_height', split_height)

def update_detection_sensitivity(detection_sensitivity: int) -> None:
    update_config_field('detection_sensitivity', detection_sensitivity)

def update_ignorable_pixels(ignorable_pixels: int) -> None:
    update_config_field('ignorable_pixels', ignorable_pixels)

def update_scan_line_step(scan_line_step: int) -> None:
    update_config_field('scan_line_step', scan_line_step)

def update_automatic_width(automatic_width: bool) -> None:
    update_config_field('automatic_width', int(automatic_width))

def update_group_format(group_format: str) -> None:
    update_config_field('group_format', group_format)

def update_group(group: bool) -> None:
    update_config_field('group_flag', int(group))

def update_group_replace_original_files(replace: bool) -> None:
    update_config_field('group_replace_original_files', int(replace))

def update_slice_replace_original_files(replace: bool) -> None:
    update_config_field('slice_replace_original_files', int(replace))