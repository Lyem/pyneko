import sqlite3
from pathlib import Path
from os import makedirs
from platformdirs import user_config_dir
from dataclasses import dataclass, asdict
import json

data_path = user_config_dir('pyneko')
db_path = Path(data_path) / 'login.db'
makedirs(data_path, exist_ok=True)

@dataclass
class LoginData:
    domain: str
    headers: dict
    cookies: dict

    def as_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS login (
                        domain TEXT PRIMARY KEY,
                        headers TEXT,
                        cookies TEXT
                      )''')
    conn.commit()
    conn.close()

def insert_login(data: LoginData) -> None:
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO login (domain, headers, cookies) VALUES (?, ?, ?)',
                   (data.domain, json.dumps(data.headers), json.dumps(data.cookies)))
    conn.commit()
    conn.close()

def get_login(domain: str) -> LoginData | None:
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM login WHERE domain = ?', (domain,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return LoginData(domain=row[0], headers=json.loads(row[1]), cookies=json.loads(row[2]))

def update_login(domain: str, headers: dict = None, cookies: dict = None) -> None:
    request_data = get_login(domain)
    if request_data is None:
        raise ValueError(f'Request with domain "{domain}" does not exist.')
    
    if headers is None:
        headers = request_data.headers
    if cookies is None:
        cookies = request_data.cookies

    updated_data = LoginData(domain=domain, headers=headers, cookies=cookies)
    insert_login(updated_data)

def delete_login(domain: str) -> None:
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM login WHERE domain = ?', (domain,))
    conn.commit()
    conn.close()
