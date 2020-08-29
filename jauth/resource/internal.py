import time
from typing import List, Optional

import deserialize
from aiohttp.web_request import Request

from jauth.decorator.internal import restrict_external_request_handler
from jauth.decorator.request import request_error_handler
from jauth.decorator.token import token_error_handler
from jauth.exception.permission import ServerKeyError
from jauth.repository.user import find_user_by_id, search_users, user_model_to_dict
from jauth.resource import json_response, convert_request
from jauth.structure.datetime_range import DatetimeRange
from jauth.structure.token.temp import VerifyUserEmailClaim, ResetPasswordClaim
from jauth.util.logger.logger import get_logger
from jauth.model.user import User, UserType

logger = get_logger(__name__)


class CreateEmailVerifyingTokenRequest:
    user_id: str


class CreatePasswordResetTokenRequest:
    user_id: str


@deserialize.default('start', 0)
@deserialize.parser('start', int)
@deserialize.default('size', 10)
@deserialize.parser('size', int)
@deserialize.default('order_bys', [])
@deserialize.default('extras', [])
@deserialize.default('emails', [])
@deserialize.default('status', [])
@deserialize.default('types', [])
class SearchUserRequest:
    emails: List[str]
    extras: List[str]
    created_at_range: Optional[DatetimeRange]
    modified_at_range: Optional[DatetimeRange]
    start: int
    size: int
    order_bys: List[str]
    status: List[int]
    types: List[int]


class InternalHttpResource:
    ACCESS_TOKEN_EXPIRE_TIME = 60 * 60  # 1 hour

    def __init__(self, router, storage, secret, external):
        self.jwt_secret = secret['jwt_secret']
        self.internal_api_keys: List[str] = secret['internal_api_keys']
        self.router = router

    def route(self):
        self.router.add_route('POST', '/users:search', self.search_users)
        self.router.add_route('POST', '/token/email_verify', self.generate_email_verifying_token)
        self.router.add_route('POST', '/token/password_reset', self.generate_password_reset_token)

    def _check_server_key(self, request: Request):
        x_server_key = request.headers.get('X-Server-Key')
        if x_server_key not in self.internal_api_keys:
            raise ServerKeyError()

    @request_error_handler
    @restrict_external_request_handler
    async def generate_email_verifying_token(self, request):
        self._check_server_key(request=request)

        request_body: CreateEmailVerifyingTokenRequest = convert_request(
            CreateEmailVerifyingTokenRequest, await request.json())
        user: User = await find_user_by_id(request_body.user_id)
        if not user:
            return json_response(
                reason=f'user not found', status=404)

        user_claim: VerifyUserEmailClaim = deserialize.deserialize(VerifyUserEmailClaim, {
            'id': str(user.id),
            'type': int(user.type),
            'exp': time.time() + self.ACCESS_TOKEN_EXPIRE_TIME,
        })
        token = user_claim.to_jwt(self.jwt_secret)

        return json_response(result=token)

    @request_error_handler
    @restrict_external_request_handler
    async def generate_password_reset_token(self, request):
        self._check_server_key(request=request)

        request_body: CreatePasswordResetTokenRequest = convert_request(
            CreatePasswordResetTokenRequest, await request.json())
        user: User = await find_user_by_id(request_body.user_id)
        if not user:
            return json_response(
                reason=f'user not found', status=404)

        if user.type != UserType.EMAIL:
            return json_response(
                reason=f'only email user can reset password', status=400)

        user_claim: ResetPasswordClaim = deserialize.deserialize(ResetPasswordClaim, {
            'id': str(user.id),
            'type': int(user.type),
            'exp': time.time() + self.ACCESS_TOKEN_EXPIRE_TIME,
        })
        token = user_claim.to_jwt(self.jwt_secret)

        return json_response(result=token)

    @request_error_handler
    @restrict_external_request_handler
    async def search_users(self, request):
        self._check_server_key(request=request)

        available_order_bys = {
            'id', '-id',
            'email', '-email',
            'created_at', '-created_at',
            'modified_at', '-modified_at'
        }

        request_body: SearchUserRequest = convert_request(
            SearchUserRequest, await request.json())

        total, users = await search_users(
            emails=request_body.emails,
            created_at_range=request_body.created_at_range,
            modified_at_range=request_body.modified_at_range,
            extra_text=request_body.extras,
            start=request_body.start,
            size=request_body.size,
            order_bys=list(available_order_bys.intersection(request_body.order_bys)),
            status=request_body.status,
            types=request_body.types,
        )
        return json_response(result={
            'total': total,
            'users': [
                user_model_to_dict(user)
                for user in users
            ]
        })
