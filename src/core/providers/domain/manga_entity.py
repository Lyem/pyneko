from dataclasses import dataclass
from core.__seedwork.domain.entities import Entity

@dataclass
class Manga(Entity):
    id: str
    name: str

    @classmethod
    def from_dict(cls, data):
        return Manga(**data)

