from dataclasses import dataclass
from core.__seedwork.domain.entities import Entity

@dataclass
class Chapter(Entity):
    id: str
    number: str
    name: str

    @classmethod
    def from_dict(id: str, number: str, name: str):
        return Chapter(id, number, name)

