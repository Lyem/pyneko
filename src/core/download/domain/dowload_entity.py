from typing import List
from dataclasses import dataclass
from core.__seedwork.domain.entities import Entity

@dataclass
class Chapter(Entity):
    number: str
    files: List[str]

    @classmethod
    def from_dict(number: str, files: List[str]):
        return Chapter(number, files)

