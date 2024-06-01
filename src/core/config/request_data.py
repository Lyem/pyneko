from dataclasses import dataclass, asdict

@dataclass
class RequestData:
    domain: str
    headers: dict
    cookies: dict

    def as_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return RequestData(**data)