import abc

from jauth.model.token import Token
from jauth.repository import BaseRepository


class TokenRepository(BaseRepository, abc.ABC):
    @abc.abstractmethod
    async def find_token_by_id(self, _id: str) -> Token:
        pass

    @abc.abstractmethod
    async def create_token(self, user_id: str) -> Token:
        pass

    @abc.abstractmethod
    async def delete_token(self, token_id: str) -> int:
        pass
