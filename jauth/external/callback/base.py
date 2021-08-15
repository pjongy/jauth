import abc
from typing import List, Tuple


class BaseCallbackHandler(abc.ABC):
    def __init__(self, urls: List[Tuple[str, str]]):
        self.urls = urls

    @abc.abstractmethod
    async def handle(self, message: dict) -> bool:
        raise NotImplemented("Implement handle")
