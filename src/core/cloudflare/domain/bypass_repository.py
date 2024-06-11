from abc import ABC, abstractmethod
from .request_entity import Request

class BypassRepository(ABC):
    @abstractmethod
    def is_cloudflare_blocking(html: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def bypass_cloudflare(url: str) -> Request:
        raise NotImplementedError()

    @abstractmethod
    def bypass_cloudflare_no_capcha(url: str) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def bypass_cloudflare_no_capcha_fetch(domain: str, url: str, background: bool) -> any:
        raise NotImplementedError()

