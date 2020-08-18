import bcrypt
import deserialize

from jauth.decorator.request import request_error_handler
from jauth.decorator.token import token_error_handler
from jauth.exception.third_party import ThirdPartyTokenVerifyError
from jauth.external.token import ThirdPartyUser
from jauth.repository.user import find_user_by_id, user_model_to_dict, find_user_by_account, \
    create_user, find_user_by_third_party_user_id, update_user
from jauth.resource import convert_request, json_response
from jauth.structure.token.user import UserClaim, get_bearer_token
from jauth.util.logger.logger import get_logger
from jauth.util.model.user import UserType, User
from jauth.util.util import is_valid_email, is_valid_password, is_valid_account

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
        self.jwt_secret = secret['jwt_secret']
        self.third_party_user_method = {
            UserType.FACEBOOK: external['third_party']['facebook'].get_user,
            UserType.KAKAO: external['third_party']['kakao'].get_user,
            UserType.APPLE: external['third_party']['apple'].get_user,
            UserType.GOOGLE: external['third_party']['google'].get_user,
        }

    def route(self):
        self.router.add_route('POST', '/email', self.create_email_user)
        self.router.add_route('POST', '/third_party', self.create_third_party_user)
        self.router.add_route('GET', '/-/self', self.get_myself)
        self.router.add_route('PUT', '/-/self', self.update_myself)
        self.router.add_route('GET', '/-/{user_id}', self.get_user)
        self.router.add_route('PUT', '/email/self/password', self.update_email_user_password)

    @token_error_handler
    @request_error_handler
    async def get_myself(self, request):
        user_info: UserClaim = get_bearer_token(self.jwt_secret, request)
        user = await find_user_by_id(user_info.id)
        if not user:
            return json_response(
                reason=f'user not found', status=404)

        return json_response(result=user_model_to_dict(user))

    @request_error_handler
    async def get_user(self, request):
        user_id = request.match_info['user_id']
        user = await find_user_by_id(user_id)
        if not user:
            return json_response(
                reason=f'user not found', status=404)

        return json_response(result=user_model_to_dict(user))

    @request_error_handler
    async def create_third_party_user(self, request):
        request_body: CreateThirdPartyUserRequest = convert_request(
            CreateThirdPartyUserRequest,
            await request.json()
        )
        try:
            get_third_party_user = self.third_party_user_method[request_body.user_type]
        except KeyError:
            return json_response(reason='invalid user type', status=400)

        try:
            third_party_user: ThirdPartyUser = await get_third_party_user(
                request_body.third_party_token)
        except ThirdPartyTokenVerifyError:
            return json_response(reason='invalid third party token', status=400)

        user: User = await find_user_by_third_party_user_id(
            third_party_user_id=third_party_user.id,
            user_type=request_body.user_type,
        )

        if user:
            return json_response(
                reason=f'account[{third_party_user.id}] already exists', status=409)

        user = await create_user(
            user_type=third_party_user.type,
            email=third_party_user.email,
            third_party_user_id=third_party_user.id,
            extra=request_body.extra,
        )
        return json_response(result=user_model_to_dict(user))

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

    @token_error_handler
    @request_error_handler
    async def update_myself(self, request):
        user_info: UserClaim = get_bearer_token(self.jwt_secret, request)
        request_body: UpdateUserRequest = convert_request(
            UpdateUserRequest,
            await request.json()
        )
        if not is_valid_email(request_body.email):
            return json_response(
                reason=f'{request_body.email} is invalid email format', status=400)

        user: User = await find_user_by_id(user_info.id)
        if not user:
            return json_response(
                reason=f'user not found', status=404)

        verified_status = {}
        if user.email != request_body.email:
            verified_status['is_email_verified'] = False

        affected_rows = await update_user(
            user_id=user_info.id,
            email=request_body.email,
            extra=request_body.extra,
            **verified_status,
        )
        return json_response(result=affected_rows > 0)

    @token_error_handler
    @request_error_handler
    async def update_email_user_password(self, request):
        user_info: UserClaim = get_bearer_token(self.jwt_secret, request)
        request_body: UpdateUserPasswordRequest = convert_request(
            UpdateUserPasswordRequest,
            await request.json()
        )
        user: User = await find_user_by_id(user_info.id)
        if not user:
            return json_response(
                reason=f'user not found', status=404)

        if user.type != UserType.EMAIL:
            return json_response(
                reason=f'only email user can update password', status=404)

        if not is_valid_password(request_body.new_password):
            return json_response(reason='password policy is not satisfied', status=400)

        if not bcrypt.checkpw(
            request_body.original_password.encode(),
            user.hashed_password.encode()
        ):
            return json_response(reason='Invalid password', status=403)

        hashed_password = bcrypt.hashpw(
            request_body.new_password.encode(),
            bcrypt.gensalt()
        ).decode()

        affected_rows = await update_user(
            user_id=user_info.id,
            hashed_password=hashed_password,
        )
        return json_response(result=affected_rows > 0)
