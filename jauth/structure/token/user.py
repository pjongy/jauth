import deserialize
from aiohttp.abc import BaseRequest

from jauth.exception.token import TokenNotDeliveredError
from jauth.structure.token.jwt import JwtClaim


@deserialize.default("iss", "jauth")
@deserialize.parser("type", int)
class UserClaim(JwtClaim):
    id: str
    type: int
    iss: str = "jauth"  # NOTE: for check issuer (class variable)


def get_bearer_token(token_secret: str, request: BaseRequest) -> UserClaim:
    bearer = "Bearer "
    auth_jwt = request.headers.get("Authorization")
    if not auth_jwt or not auth_jwt.startswith(bearer):
        raise TokenNotDeliveredError

    token = auth_jwt[len(bearer) :]
    return UserClaim.from_jwt(token, token_secret)
