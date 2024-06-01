from dataclasses import asdict
from abc import abstractmethod

class Entity():

    def as_dict(self):
        return asdict(self)
    @abstractmethod
    def from_dict(cls, self):
        raise NotImplementedError()
