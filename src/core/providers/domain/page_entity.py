from typing import List
from dataclasses import dataclass
from core.__seedwork.domain.entities import Entity

@dataclass
class Pages(Entity):
    id: str
    number: str
    name: str
    pages: List[str]

    @classmethod
    def from_dict(id: str, number: str, name: str, pages: List[str]):
        return Pages(id, number, name, pages)

