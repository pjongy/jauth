import bcrypt
import deserialize

from apiserver.decorator.request import request_error_handler
from apiserver.repository.user import find_user_by_id, user_model_to_dict, find_user_by_account, \
    create_user
from apiserver.resource import convert_request, json_response
from common.logger.logger import get_logger
from common.model.user import UserType
from common.util import is_valid_email, is_valid_password, is_valid_account

logger = get_logger(__name__)


@deserialize.default('extra', {})
class CreateEmailUserRequest:
    account: str
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
        request_body: CreateThirdPartyUserRequest = convert_request(
            CreateThirdPartyUserRequest,
            await request.json()
        )
        # TODO: Create third party user by user_id and response user information

    @request_error_handler
    async def create_email_user(self, request):
        request_body: CreateEmailUserRequest = convert_request(
            CreateEmailUserRequest,
            await request.json()
        )

        user = await find_user_by_account(request_body.account)
        if user:
            return json_response(
                reason=f'account[{request_body.account}] already exists', status=409)

        if not is_valid_account(request_body.account):
            return json_response(
                reason=f'{request_body.account} is invalid account format', status=400)

        if not is_valid_email(request_body.email):
            return json_response(
                reason=f'{request_body.email} is invalid email format', status=400)

        if not is_valid_password(request_body.password):
            return json_response(reason='password policy is not satisfied', status=400)

        hashed_password = bcrypt.hashpw(
            request_body.password.encode(),
            bcrypt.gensalt()
        ).decode()
        user = await create_user(
            user_type=UserType.EMAIL,
            account=request_body.account,
            hashed_password=hashed_password,
            email=request_body.email,
            extra=request_body.extra,
        )
        return json_response(result=user_model_to_dict(user))

    @request_error_handler
    async def update_user(self, request):
        user_id = request.match_info['user_id']
        request_body: UpdateUserRequest = convert_request(
            UpdateUserRequest,
            await request.json()
        )
        # TODO: Create user by user_id and response user information

    @request_error_handler
    async def update_email_user_password(self, request):
        user_id = request.match_info['user_id']
        request_body: UpdateUserPasswordRequest = convert_request(
            UpdateUserPasswordRequest,
            await request.json()
        )
        # TODO: Update email user password
