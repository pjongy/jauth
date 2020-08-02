import deserialize

from apiserver.exception.third_party import ThirdPartyTokenVerifyError
from apiserver.external.token import ThirdPartyUser
from common.request import Request
from common.model.user import UserType


@deserialize.default('email', '')
@deserialize.default('email_verified', False)
@deserialize.default('name', '')
@deserialize.default('picture', '')
@deserialize.default('locale', '')
class GoogleUser:
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
            'id': google_user.id,
            'type': UserType.GOOGLE,
            'name': google_user.name,
            'image_url': google_user.picture,
            'is_email_verified': google_user.email_verified,
        })
