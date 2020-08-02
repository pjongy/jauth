import deserialize

from apiserver.decorator.request import request_error_handler
from apiserver.resource import convert_request
from common.logger.logger import get_logger

logger = get_logger(__name__)


@deserialize.default('extra', {})
class CreateEmailUserRequest:
    email: str
    password: str
    extra: dict


@deserialize.default('extra', {})
@deserialize.parser('user_type', UserType)
class CreateThirdPartyUserRequest:
    user_type: UserType
    third_party_token: str
    extra: dict


class UpdateUserRequest:
    email: str
    extra: dict


class UpdateUserPasswordRequest:
    original_password: str
    new_password: str


class UsersHttpResource:
    def __init__(self, router, storage, secret, external):
        self.router = router

    def route(self):
        self.router.add_route('POST', '/email', self.create_email_user)
        self.router.add_route('POST', '/third_party', self.create_third_party_user)
        self.router.add_route('GET', '/-/{user_id}', self.get_user)
        self.router.add_route('PUT', '/-/{user_id}', self.update_user)
        self.router.add_route('PUT', '/email/{user_id}/password', self.update_email_user_password)

    @request_error_handler
    async def get_user(self, request):
        user_id = request.match_info['user_id']
        # TODO: Find user by user_id and response user information

    @request_error_handler
    async def create_third_party_user(self, request):
        request: CreateEmailUserRequest = convert_request(
            CreateEmailUserRequest,
            await request.json()
        )
        # TODO: Create third party user by user_id and response user information

    @request_error_handler
    async def create_email_user(self, request):
        request: CreateThirdPartyUserRequest = convert_request(
            CreateThirdPartyUserRequest,
            await request.json()
        )
        # TODO: Create email user by user_id and response user information

    @request_error_handler
    async def update_user(self, request):
        user_id = request.match_info['user_id']
        request: UpdateUserRequest = convert_request(
            UpdateUserRequest,
            await request.json()
        )
        # TODO: Create user by user_id and response user information

    @request_error_handler
    async def update_email_user_password(self, request):
        user_id = request.match_info['user_id']
        request: UpdateUserPasswordRequest = convert_request(
            UpdateUserPasswordRequest,
            await request.json()
        )
        # TODO: Update email user password
