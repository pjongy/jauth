import deserialize

from jauth.exception.third_party import ThirdPartyTokenVerifyError
from jauth.external.token import ThirdPartyUser
from jauth.util import Request
from jwcrypto import jwt, jwk
import jwt as pyjwt

from jauth.util.model.user import UserType


@deserialize.default('iss', '')
@deserialize.default('sub', '')
@deserialize.default('aud', '')
@deserialize.default('email', '')
@deserialize.default('is_private_email', False)
@deserialize.default('email_verified', False)
class AppleUser:
    iss: str
    sub: str
    aud: str
    email: str
    is_private_email: bool
    email_verified: bool


class AppleToken(Request):
    JWK_HOST = 'https://appleid.apple.com'
    JWK_RESOURCE = '/auth/keys'

    async def _get_jwk_sets(self):
        status, response, _ = await self.get(
            url=f'{self.JWK_HOST}{self.JWK_RESOURCE}'
        )

        if not 200 <= status < 300:
            raise ThirdPartyTokenVerifyError(f'status is not OK: {status} / {response}')

        key_sets = response['keys']
        public_keys = {}
        for key in key_sets:
            public_keys[key['kid']] = key

        return public_keys

    async def get_user(self, token) -> ThirdPartyUser:
        public_keys = await self._get_jwk_sets()
        key_id = pyjwt.get_unverified_header(token)['kid']

        jwt_public_key = public_keys[key_id]
        apple_jwk = jwk.JWK(**jwt_public_key)
        try:
            apple_jwt = jwt.JWT(key=apple_jwk, jwt=token)
        except BaseException:
            raise ThirdPartyTokenVerifyError("invalid jwt")

        apple_user: AppleUser = deserialize.deserialize(
            AppleUser, jwt.json_decode(apple_jwt.claims))

        return deserialize.deserialize(ThirdPartyUser, {
            'email': apple_user.email,
            'id': apple_user.sub,
            'type': UserType.APPLE,
            'is_email_verified': apple_user.email_verified,
        })
