from uuid import UUID

from tortoise import fields
from tortoise.models import Model

from jauth.model.mixin import TimestampMixin


class Token(Model, TimestampMixin):
    class Meta:
        table = 'token'

    id: UUID = fields.UUIDField(pk=True)
    user_id: UUID = fields.UUIDField()
