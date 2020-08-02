import deserialize

from apiserver.exception.thirdparty import ThirdPartyTokenVerifyError
from apiserver.external.token import ThirdPartyUser
from common.request import Request
from common.model.user import UserType
from common.structure import default_object


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
class KakaoUserAccount:
    profile: KakaoUserProfile
    profile_needs_agreement: bool
    email: str


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

        kakao_user = deserialize.deserialize(KakaoUser, response)

        return deserialize.deserialize(ThirdPartyUser, {
            'email': kakao_user.kakao_account.email,
            'third_party_user_id': kakao_user.id,
            'type': UserType.KAKAO,
            'name': kakao_user.kakao_account.profile.nickname,
            'image_url': kakao_user.kakao_account.profile.profile_image_url,
        })