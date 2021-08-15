import abc
from typing import List, Tuple

from jauth.model.user import User, UserType
from jauth.repository import BaseRepository
from jauth.structure.datetime_range import DatetimeRange


class UserRepository(BaseRepository, abc.ABC):
    @abc.abstractmethod
    async def find_user_by_id(self, _id: str) -> User:
        pass

    @abc.abstractmethod
    async def find_user_by_account(self, account: str) -> User:
        pass

    @abc.abstractmethod
    async def find_user_by_third_party_user_id(
        self, user_type: UserType, third_party_user_id: str
    ) -> User:
        pass

    @abc.abstractmethod
    async def search_users(
        self,
        emails: List[str] = (),
        created_at_range: DatetimeRange = None,
        modified_at_range: DatetimeRange = None,
        extra_text: List[str] = (),
        start: int = 0,
        size: int = 10,
        order_bys: List[str] = (),
        status: List[int] = (),
        types: List[int] = (),
    ) -> Tuple[int, List[User]]:
        pass

    @abc.abstractmethod
    async def create_user(
        self,
        user_type: UserType,
        email: str,
        account: str = None,
        hashed_password: str = None,
        third_party_user_id: str = None,
        extra: dict = None,
    ) -> User:
        pass

    @abc.abstractmethod
    async def update_user(self, user_id: str, **kwargs) -> int:
        pass
