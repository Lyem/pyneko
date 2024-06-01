from dataclasses import dataclass, asdict
from core.providers.domain.manga_entity import Manga
from typing import List

@dataclass
class MangasCache:
    domain: str
    mangas: List[Manga]

    def as_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        mangas_list = []
        for manga in data['mangas']:
            mangas_list.append(Manga.from_dict(manga))
        return MangasCache(domain=data['domain'], mangas=mangas_list)