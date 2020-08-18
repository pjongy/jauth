import enum
from uuid import UUID

from tortoise import fields
from tortoise.models import Model

from jauth.model.mixin import TimestampMixin


class UserType(enum.IntEnum):
    UNKNOWN = 0
    EMAIL = 1
    GOOGLE = 2
    APPLE = 3
    FACEBOOK = 4
    KAKAO = 5


class UserStatus(enum.IntEnum):
    NORMAL = 0
    DELETED = 1
    WITHDRAWN = 2


class User(Model, TimestampMixin):
    class Meta:
        table = 'user'

    id: UUID = fields.UUIDField(pk=True)
    email = fields.CharField(max_length=255)
    account = fields.CharField(max_length=64, null=True)
    hashed_password = fields.CharField(max_length=64, null=True)
    third_party_user_id = fields.TextField(null=True)
    type = fields.IntEnumField(UserType)
    status = fields.IntEnumField(UserStatus, default=UserStatus.NORMAL)
    is_email_verified = fields.BooleanField(default=False)
    extra = fields.JSONField(default={})
