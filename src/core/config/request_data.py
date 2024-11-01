import sqlite3
from pathlib import Path
from os import makedirs
from platformdirs import user_config_dir
from dataclasses import dataclass, asdict
import json

data_path = user_config_dir('pyneko')
db_path = Path(data_path) / 'requests.db'
makedirs(data_path, exist_ok=True)

@dataclass
class RequestData:
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
                        domain TEXT PRIMARY KEY,
                        headers TEXT,
                        cookies TEXT
                      )''')
    conn.commit()
    conn.close()

def insert_request(data: RequestData) -> None:
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO requests (domain, headers, cookies) VALUES (?, ?, ?)',
                   (data.domain, json.dumps(data.headers), json.dumps(data.cookies)))
    conn.commit()
    conn.close()

def get_request(domain: str) -> RequestData | None:
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM requests WHERE domain = ?', (domain,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return RequestData(domain=row[0], headers=json.loads(row[1]), cookies=json.loads(row[2]))

def update_request(domain: str, headers: dict = None, cookies: dict = None) -> None:
    request_data = get_request(domain)
    if request_data is None:
        raise ValueError(f'Request with domain "{domain}" does not exist.')
    
    if headers is None:
        headers = request_data.headers
    if cookies is None:
        cookies = request_data.cookies

    updated_data = RequestData(domain=domain, headers=headers, cookies=cookies)
    insert_request(updated_data)

def delete_request(domain: str) -> None:
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM requests WHERE domain = ?', (domain,))
    conn.commit()
    conn.close()
