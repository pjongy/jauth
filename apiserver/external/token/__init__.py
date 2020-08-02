import deserialize

from common.model.user import UserType


@deserialize.default('name', '')
@deserialize.default('email', '')
@deserialize.default('third_party_user_id', '')
@deserialize.default('image_url', '')
@deserialize.parser('id', str)
class ThirdPartyUser:
    name: str
    email: str
    third_party_user_id: str
    image_url: str
    type: UserType
