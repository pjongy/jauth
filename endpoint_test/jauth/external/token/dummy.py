import deserialize

from jauth.exception.third_party import ThirdPartyTokenVerifyError
from jauth.external.token import ThirdPartyUser
from jauth.model.user import UserType


class DummyThirdPartyRequest:
    def __init__(self, available_third_party_tokens: dict, user_type: UserType):
        self.available_third_party_tokens = available_third_party_tokens
        self.user_type = user_type

    async def get_user(self, external_token: str) -> ThirdPartyUser:
        if external_token not in self.available_third_party_tokens:
            raise ThirdPartyTokenVerifyError("invalid third party token")
        return deserialize.deserialize(
            ThirdPartyUser,
            {
                "id": self.available_third_party_tokens[external_token],
                "name": "dummy user",
                "email": "dummy@user.com",
                "image_url": "dummy.png",
                "is_email_verified": False,
                "type": self.user_type,
            },
        )
