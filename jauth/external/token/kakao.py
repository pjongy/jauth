import deserialize

from jauth.exception.third_party import ThirdPartyTokenVerifyError
from jauth.external.token import ThirdPartyUser
from jauth.util import Request
from jauth.util.model.user import UserType
from jauth.util.structure import default_object


@deserialize.default('thumbnail_image_url', '')
@deserialize.default('nickname', '')
@deserialize.default('profile_image_url', '')
class KakaoUserProfile:
    thumbnail_image_url: str
    nickname: str
    profile_image_url: str


@deserialize.default('profile', default_object(KakaoUserProfile))
@deserialize.default('profile_needs_agreement', False)
@deserialize.default('email', '')
@deserialize.default('is_email_valid', False)
@deserialize.default('is_email_verified', False)
class KakaoUserAccount:
    profile: KakaoUserProfile
    profile_needs_agreement: bool
    email: str
    is_email_valid: bool
    is_email_verified: bool


@deserialize.default('thumbnail_image', '')
@deserialize.default('nickname', '')
@deserialize.default('profile_image', '')
class KakaoUserProperties:
    thumbnail_image: str
    nickname: str
    profile_image: str


@deserialize.default('id', 0)
@deserialize.default('kakao_account', default_object(KakaoUserAccount))
@deserialize.default('properties', default_object(KakaoUserProperties))
class KakaoUser:
    id: int
    kakao_account: KakaoUserAccount
    properties: KakaoUserProperties


class KakaoToken(Request):
    API_HOST = 'https://kapi.kakao.com'
    USER_RESOURCE = '/v2/user/me'

    async def get_user(self, token) -> ThirdPartyUser:
        headers = {
            **self.DEFAULT_HEADERS,
            'Authorization': f'Bearer {token}'
        }
        status, response, _ = await self.get(
            url=f'{self.API_HOST}{self.USER_RESOURCE}',
            headers=headers
        )

        if not 200 <= status < 300:
            raise ThirdPartyTokenVerifyError(f'Status is not OK: {status} / {response}')

        kakao_user: KakaoUser = deserialize.deserialize(KakaoUser, response)
        kakao_account = kakao_user.kakao_account
        return deserialize.deserialize(ThirdPartyUser, {
            'email': kakao_account.email,
            'id': kakao_user.id,
            'type': UserType.KAKAO,
            'name': kakao_account.profile.nickname,
            'image_url': kakao_account.profile.profile_image_url,
            'is_email_verified': kakao_account.is_email_verified and kakao_account.is_email_valid
        })
