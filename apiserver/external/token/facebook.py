import deserialize

from apiserver.exception.third_party import ThirdPartyTokenVerifyError
from apiserver.external.token import ThirdPartyUser
from common.request import Request
from common.model.user import UserType
from common.structure import default_object


@deserialize.default('url', '')
@deserialize.default('height', 0)
@deserialize.default('width', 0)
@deserialize.default('is_silhouette', False)
class FacebookImageData:
    url: str
    height: int
    width: int
    is_silhouette: bool


@deserialize.default('data', default_object(FacebookImageData))
class FacebookImage:
    data: FacebookImageData


@deserialize.default('message', '')
@deserialize.default('type', '')
@deserialize.default('code', 0)
@deserialize.default('fbtrace_id', '')
class FacebookError:
    message: str
    type: str
    code: int
    fbtrace_id: str


@deserialize.default('error', default_object(FacebookError))
@deserialize.default('name', '')
@deserialize.default('id', '')
@deserialize.default('email', '')
@deserialize.default('picture', default_object(FacebookImage))
class FacebookUser:
    error: FacebookError
    name: str
    id: str
    email: str
    picture: FacebookImage


class FacebookToken(Request):
    API_HOST = 'https://graph.facebook.com'
    USER_RESOURCE = '/v5.0/me'

    async def get_user(self, token) -> ThirdPartyUser:
        status, response, _ = await self.get(
            url=f'{self.API_HOST}{self.USER_RESOURCE}',
            parameters={
                'fields': 'picture,name,id,email',
                'access_token': token
            }
        )

        if not 200 <= status < 300:
            raise ThirdPartyTokenVerifyError(f'Status is not OK: {status} / {response}')

        facebook_user = deserialize.deserialize(FacebookUser, response)

        return deserialize.deserialize(ThirdPartyUser, {
            'email': facebook_user.email,
            'third_party_user_id': facebook_user.id,
            'type': UserType.FACEBOOK,
            'name': facebook_user.name,
            'image_url': facebook_user.picture.data.url,
        })
