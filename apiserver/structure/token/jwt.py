import time

import deserialize
import jwt
from jwt import PyJWTError

from apiserver.exception.token import InvalidTokenException, TokenExpiredException
from common.util import object_to_dict


@deserialize.parser('exp', int)
class JwtClaim:
    exp: int
    iss: str

    def is_expired(self) -> bool:
        return self.exp < time.time()

    def to_jwt(self, secret) -> str:
        return jwt.encode(
            object_to_dict(self),
            secret,
            algorithm='HS256',
        ).decode()

    @classmethod
    def from_jwt(cls, token, secret):
        try:
            token_info = jwt.decode(token, secret, algorithms=['HS256'])
        except PyJWTError:
            raise InvalidTokenException

        if token_info.get('iss') != cls.iss:
            raise InvalidTokenException

        token_object = deserialize.deserialize(cls, token_info)

        if token_object.is_expired():
            raise TokenExpiredException

        return token_object
