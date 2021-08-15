import abc

from tortoise.queryset import QuerySet

from jauth.model.token import Token
from jauth.repository.token_base import TokenRepository


def _token_relational_query_set(query_set: QuerySet[Token]) -> QuerySet[Token]:
    return query_set


class TokenRepositoryImpl(TokenRepository):
    async def find_token_by_id(self, _id: str) -> Token:
        return await _token_relational_query_set(
            Token.filter(id=_id).order_by("modified_at", "created_at")
        ).first()

    async def create_token(self, user_id: str) -> Token:
        return await Token.create(user_id=user_id)

    async def delete_token(self, token_id: str) -> int:
        return await _token_relational_query_set(
            Token.filter(id=token_id).order_by("modified_at", "created_at")
        ).delete()
