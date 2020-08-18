import time
from typing import List

import deserialize
from aiohttp.web_request import Request

from jauth.decorator.internal import restrict_external_request_handler
from jauth.decorator.request import request_error_handler
from jauth.decorator.token import token_error_handler
from jauth.exception.permission import ServerKeyError
from jauth.repository.user import find_user_by_id
from jauth.resource import json_response, convert_request
from jauth.structure.token.temp import VerifyUserEmailClaim
from jauth.util.logger.logger import get_logger
from jauth.model.user import User

logger = get_logger(__name__)


class CreateEmailVerifyingTokenRequest:
    user_id: str


class InternalHttpResource:
    ACCESS_TOKEN_EXPIRE_TIME = 60 * 60  # 1 hour

    def __init__(self, router, storage, secret, external):
        self.jwt_secret = secret['jwt_secret']
        self.internal_api_keys: List[str] = secret['internal_api_keys']
        self.router = router

    def route(self):
        self.router.add_route('POST', '/token/email_verify', self.generate_email_verifying_token)

    def _check_server_key(self, request: Request):
        x_server_key = request.headers.get('X-Server-Key')
        if x_server_key not in self.internal_api_keys:
            raise ServerKeyError()

    def _create_access_token(self, user: User) -> str:
        user_claim: VerifyUserEmailClaim = deserialize.deserialize(VerifyUserEmailClaim, {
            'id': str(user.id),
            'type': int(user.type),
            'exp': time.time() + self.ACCESS_TOKEN_EXPIRE_TIME,
        })
        return user_claim.to_jwt(self.jwt_secret)

    @token_error_handler
    @request_error_handler
    @restrict_external_request_handler
    async def generate_email_verifying_token(self, request):
        self._check_server_key(request=request)

        request_body: CreateEmailVerifyingTokenRequest = convert_request(
            CreateEmailVerifyingTokenRequest, await request.json())
        user: User = await find_user_by_id(request_body.user_id)
        token = self._create_access_token(user)
        return json_response(result=token)
