from abc import ABC, abstractmethod
import json
from urllib.parse import urljoin

class Response:
    def __init__(self, status: int, data: str, content, url):
        self.status = status
        self.data = data
        self.content = content
        self.url = url
    
    def text(self):
        return str(self.content)
    
    def json(self):
        return json.loads(self.data)

class Http(ABC):

    @abstractmethod
    def get(url: str, params=None, **kwargs) -> Response:
        raise NotImplementedError()
    
    @abstractmethod
    def post(url, data=None, json=None, **kwargs) -> Response:
        raise NotImplementedError()