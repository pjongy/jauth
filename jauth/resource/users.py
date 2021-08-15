import bcrypt
import deserialize
from aiohttp.web_urldispatcher import UrlDispatcher

from jauth.decorator.request import request_error_handler
from jauth.decorator.token import token_error_handler
from jauth.exception.third_party import ThirdPartyTokenVerifyError
from jauth.external.callback.base import BaseCallbackHandler
from jauth.external.callback.user_create import UserCreationCallbackHandler
from jauth.external.callback.user_update import UserUpdateCallbackHandler
from jauth.external.token import ThirdPartyUser
from jauth.repository.user import user_model_to_dict
from jauth.repository.user_base import UserRepository
from jauth.resource import convert_request, json_response
from jauth.resource.base import BaseResource
from jauth.structure.token.temp import VerifyUserEmailClaim, ResetPasswordClaim
from jauth.structure.token.user import UserClaim, get_bearer_token
from jauth.util.logger.logger import get_logger
from jauth.model.user import UserType, User, UserStatus
from jauth.util.util import is_valid_email, is_valid_password, is_valid_account

logger = get_logger(__name__)


@deserialize.default("extra", {})
class CreateEmailUserRequest:
    account: str
    email: str
    password: str
    extra: dict


@deserialize.default("extra", {})
@deserialize.parser("user_type", UserType)
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


class VerifyEmailRequest:
    temp_token: str


class ResetPasswordRequest:
    temp_token: str
    new_password: str


class UsersHttpResource(BaseResource):
    def __init__(
        self,
        user_creation_callback_handler: BaseCallbackHandler,
        user_update_callback_handler: BaseCallbackHandler,
        user_repository: UserRepository,
        secret: dict,
        external: dict,
    ):
        self.user_creation_callback_handler = user_creation_callback_handler
        self.user_update_callback_handler = user_update_callback_handler
        self.user_repository = user_repository
        self.jwt_secret = secret["jwt_secret"]
        self.third_party_user_method = {
            UserType.FACEBOOK: external["third_party"]["facebook"].get_user,
            UserType.KAKAO: external["third_party"]["kakao"].get_user,
            UserType.APPLE: external["third_party"]["apple"].get_user,
            UserType.GOOGLE: external["third_party"]["google"].get_user,
        }

    def route(self, router: UrlDispatcher):
        router.add_route("POST", "/email", self.create_email_user)
        router.add_route("POST", "/third_party", self.create_third_party_user)
        router.add_route("GET", "/-/self", self.get_myself)
        router.add_route("PUT", "/-/self", self.update_myself)
        router.add_route("GET", "/-/{user_id}", self.get_user)
        router.add_route("POST", "/-/self:verify", self.verify_myself)
        router.add_route("PUT", "/email/self/password", self.update_email_user_password)
        router.add_route(
            "POST", "/email/self/password:reset", self.reset_email_user_password
        )

    @request_error_handler
    @token_error_handler
    async def get_myself(self, request):
        user_info: UserClaim = get_bearer_token(self.jwt_secret, request)
        user = await self.user_repository.find_user_by_id(user_info.id)
        if not user:
            return json_response(reason=f"user not found", status=404)

        return json_response(result=user_model_to_dict(user))

    @request_error_handler
    async def get_user(self, request):
        user_id = request.match_info["user_id"]
        user = await self.user_repository.find_user_by_id(user_id)
        if not user:
            return json_response(reason=f"user not found", status=404)

        return json_response(result=user_model_to_dict(user))

    async def _send_user_creation_event(self, user: User):
        user_type_to_str_map = {
            UserType.EMAIL: "EMAIL",
            UserType.KAKAO: "KAKAO",
            UserType.FACEBOOK: "FACEBOOK",
            UserType.GOOGLE: "GOOGLE",
            UserType.APPLE: "APPLE",
        }

        user_status_to_str_map = {
            UserStatus.NORMAL: "NORMAL",
            UserStatus.DELETED: "DELETED",
            UserStatus.WITHDRAWN: "WITHDRAWN",
        }

        await self.user_creation_callback_handler.handle(
            {
                "id": user.id,
                "email": user.email,
                "third_party_user_id": user.third_party_user_id,
                "type": user_type_to_str_map[user.type],
                "status": user_status_to_str_map[user.status],
                "is_email_verified": user.is_email_verified,
                "extra": user.extra,
            }
        )

    async def _send_user_update_event(self, original: User, delta: dict):
        user_status_to_str_map = {
            UserStatus.NORMAL: "NORMAL",
            UserStatus.DELETED: "DELETED",
            UserStatus.WITHDRAWN: "WITHDRAWN",
        }

        await self.user_update_callback_handler.handle(
            {
                "id": original.id,
                "email": original.email,
                "status": user_status_to_str_map[original.status],
                "is_email_verified": original.is_email_verified,
                "extra": original.extra,
            }
            | delta
        )

    @request_error_handler
    async def create_third_party_user(self, request):
        request_body: CreateThirdPartyUserRequest = convert_request(
            CreateThirdPartyUserRequest, await request.json()
        )
        try:
            get_third_party_user = self.third_party_user_method[request_body.user_type]
        except KeyError:
            return json_response(reason="invalid user type", status=400)

        try:
            third_party_user: ThirdPartyUser = await get_third_party_user(
                request_body.third_party_token
            )
        except ThirdPartyTokenVerifyError:
            return json_response(reason="invalid third party token", status=400)

        user: User = await self.user_repository.find_user_by_third_party_user_id(
            third_party_user_id=third_party_user.id,
            user_type=request_body.user_type,
        )

        if user:
            return json_response(
                reason=f"account[{third_party_user.id}] already exists", status=409
            )

        user = await self.user_repository.create_user(
            user_type=third_party_user.type,
            email=third_party_user.email,
            third_party_user_id=third_party_user.id,
            extra=request_body.extra,
        )
        await self._send_user_creation_event(user)
        return json_response(result=user_model_to_dict(user))

    @request_error_handler
    async def create_email_user(self, request):
        request_body: CreateEmailUserRequest = convert_request(
            CreateEmailUserRequest, await request.json()
        )

        user = await self.user_repository.find_user_by_account(request_body.account)
        if user:
            return json_response(
                reason=f"account[{request_body.account}] already exists", status=409
            )

        if not is_valid_account(request_body.account):
            return json_response(
                reason=f"{request_body.account} is invalid account format", status=400
            )

        if not is_valid_email(request_body.email):
            return json_response(
                reason=f"{request_body.email} is invalid email format", status=400
            )

        if not is_valid_password(request_body.password):
            return json_response(reason="password policy is not satisfied", status=400)

        hashed_password = bcrypt.hashpw(
            request_body.password.encode(), bcrypt.gensalt()
        ).decode()
        user = await self.user_repository.create_user(
            user_type=UserType.EMAIL,
            account=request_body.account,
            hashed_password=hashed_password,
            email=request_body.email,
            extra=request_body.extra,
        )
        await self._send_user_creation_event(user)
        return json_response(result=user_model_to_dict(user))

    @request_error_handler
    @token_error_handler
    async def update_myself(self, request):
        user_info: UserClaim = get_bearer_token(self.jwt_secret, request)
        request_body: UpdateUserRequest = convert_request(
            UpdateUserRequest, await request.json()
        )
        if not is_valid_email(request_body.email):
            return json_response(
                reason=f"{request_body.email} is invalid email format", status=400
            )

        user: User = await self.user_repository.find_user_by_id(user_info.id)
        if not user:
            return json_response(reason=f"user not found", status=404)

        verified_status = {}
        if user.email != request_body.email:
            verified_status["is_email_verified"] = False

        affected_rows = await self.user_repository.update_user(
            user_id=user_info.id,
            email=request_body.email,
            extra=request_body.extra,
            **verified_status,
        )

        await self._send_user_update_event(
            original=user,
            delta={
                "email": request_body.email,
                "extra": request_body.extra,
                "is_email_verified": False,
            },
        )
        return json_response(result=affected_rows > 0)

    @request_error_handler
    @token_error_handler
    async def verify_myself(self, request):
        request_body: VerifyEmailRequest = convert_request(
            VerifyEmailRequest, await request.json()
        )
        user_info: VerifyUserEmailClaim = VerifyUserEmailClaim.from_jwt(
            request_body.temp_token, self.jwt_secret
        )
        user: User = await self.user_repository.find_user_by_id(user_info.id)

        if not user:
            return json_response(reason=f"user not found", status=404)

        await self.user_repository.update_user(
            user_id=user_info.id,
            is_email_verified=True,
        )
        await self._send_user_update_event(
            original=user,
            delta={
                "is_email_verified": True,
            },
        )
        return json_response(result=True)

    @request_error_handler
    @token_error_handler
    async def update_email_user_password(self, request):
        user_info: UserClaim = get_bearer_token(self.jwt_secret, request)
        request_body: UpdateUserPasswordRequest = convert_request(
            UpdateUserPasswordRequest, await request.json()
        )
        user: User = await self.user_repository.find_user_by_id(user_info.id)
        if not user:
            return json_response(reason=f"user not found", status=404)

        if user.type != UserType.EMAIL:
            return json_response(
                reason=f"only email user can update password", status=404
            )

        if not is_valid_password(request_body.new_password):
            return json_response(reason="password policy is not satisfied", status=400)

        if not bcrypt.checkpw(
            request_body.original_password.encode(), user.hashed_password.encode()
        ):
            return json_response(reason="Invalid password", status=403)

        hashed_password = bcrypt.hashpw(
            request_body.new_password.encode(), bcrypt.gensalt()
        ).decode()

        affected_rows = await self.user_repository.update_user(
            user_id=user_info.id,
            hashed_password=hashed_password,
        )
        return json_response(result=affected_rows > 0)

    @request_error_handler
    @token_error_handler
    async def reset_email_user_password(self, request):
        request_body: ResetPasswordRequest = convert_request(
            ResetPasswordRequest, await request.json()
        )
        user_info: ResetPasswordClaim = ResetPasswordClaim.from_jwt(
            request_body.temp_token, self.jwt_secret
        )

        if user_info.type != UserType.EMAIL:
            return json_response(
                reason=f"only email user can reset password", status=400
            )

        if not is_valid_password(request_body.new_password):
            return json_response(reason="password policy is not satisfied", status=400)

        hashed_password = bcrypt.hashpw(
            request_body.new_password.encode(), bcrypt.gensalt()
        ).decode()

        affected_rows = await self.user_repository.update_user(
            user_id=user_info.id,
            hashed_password=hashed_password,
        )
        return json_response(result=affected_rows > 0)
