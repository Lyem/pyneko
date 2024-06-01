from dataclasses import dataclass
from core.__seedwork.domain.entities import Entity

@dataclass
class Request(Entity):
    user_agent: dict
    cloudflare_cookie_value: dict

    @classmethod
    def from_dict(user_agent: dict, cloudflare_cookie_value: dict):
        return Request(user_agent, cloudflare_cookie_value)
