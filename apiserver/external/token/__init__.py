import deserialize

from common.model.user import UserType


@deserialize.default('id', '')
@deserialize.default('name', '')
@deserialize.default('email', '')
@deserialize.default('image_url', '')
@deserialize.parser('id', str)
class ThirdPartyUser:
    id: str
    name: str
    email: str
    image_url: str
    type: UserType
