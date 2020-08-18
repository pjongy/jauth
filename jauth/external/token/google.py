import deserialize

from jauth.exception.third_party import ThirdPartyTokenVerifyError
from jauth.external.token import ThirdPartyUser
from jauth.util import Request
from jauth.util.model.user import UserType


@deserialize.default('sub', '')
@deserialize.default('email', '')
@deserialize.default('email_verified', False)
@deserialize.default('name', '')
@deserialize.default('picture', '')
@deserialize.default('locale', '')
class GoogleUser:
    sub: str
    email: str
    email_verified: bool
    name: str
    picture: str
    locale: str


class GoogleToken(Request):
    API_HOST = 'https://oauth2.googleapis.com'
    USER_RESOURCE = '/tokeninfo'

    async def get_user(self, token) -> ThirdPartyUser:
        status, response, _ = await self.get(
            url=f'{self.API_HOST}{self.USER_RESOURCE}',
            parameters={
                'id_token': token,
            }
        )

        if not 200 <= status < 300:
            raise ThirdPartyTokenVerifyError(f'Status is not OK: {status} / {response}')

        google_user: GoogleUser = deserialize.deserialize(GoogleUser, response)

        return deserialize.deserialize(ThirdPartyUser, {
            'email': google_user.email,
            'id': google_user.sub,
            'type': UserType.GOOGLE,
            'name': google_user.name,
            'image_url': google_user.picture,
            'is_email_verified': google_user.email_verified,
        })
