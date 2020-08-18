import asyncio
import time
import uuid

import bcrypt
import deserialize
from aioredis import ConnectionsPool

from jauth.decorator.request import request_error_handler
from jauth.decorator.token import token_error_handler
from jauth.exception.third_party import ThirdPartyTokenVerifyError
from jauth.external.token import ThirdPartyUser
from jauth.repository.user import find_user_by_third_party_user_id, find_user_by_id, \
    find_user_by_account
from jauth.resource import json_response, convert_request
from jauth.structure.token.user import UserClaim, get_bearer_token
from jauth.util.logger.logger import get_logger
from jauth.util.model.user import UserType, User
from jauth.util.util import object_to_dict, to_string

logger = get_logger(__name__)


class CreateEmailUserTokenRequest:
    account: str
    password: str


@deserialize.parser('user_type', UserType)
class CreateThirdPartyUserTokenRequest:
    user_type: UserType
    third_party_token: str


class RefreshTokenRequest:
    refresh_token: str


class TokenHttpResource:
    ACCESS_TOKEN_EXPIRE_TIME = 60 * 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_TIME = 30 * 24 * 60 * 60  # 30 days

    def __init__(self, router, storage, secret, external):
        self.third_party_user_method = {
            UserType.FACEBOOK: external['third_party']['facebook'].get_user,
            UserType.KAKAO: external['third_party']['kakao'].get_user,
            UserType.APPLE: external['third_party']['apple'].get_user,
            UserType.GOOGLE: external['third_party']['google'].get_user,
        }
        self.jwt_secret = secret['jwt_secret']
        self.redis_auth: ConnectionsPool = storage['redis']['token_cache']
        self.router = router

    def route(self):
        self.router.add_route('PUT', '', self.put)
        self.router.add_route('POST', '/third_party', self.create_third_party_user_token)
        self.router.add_route('POST', '/email', self.create_email_user_token)
        self.router.add_route('GET', '/self', self.get)

    async def set_refresh_token(self, refresh_token: str, user_id: str):
        with await self.redis_auth as conn:
            await asyncio.gather(
                conn.execute('set', refresh_token, user_id),
                conn.execute('expire', refresh_token, self.REFRESH_TOKEN_EXPIRE_TIME)
            )

    async def get_user_id_by_refresh_token(self, refresh_token):
        with await self.redis_auth as conn:
            return await conn.execute('get', refresh_token)

    def _create_access_token(self, user: User) -> str:
        user_claim: UserClaim = deserialize.deserialize(UserClaim, {
            'id': str(user.id),
            'type': int(user.type),
            'exp': time.time() + self.ACCESS_TOKEN_EXPIRE_TIME,
        })
        return user_claim.to_jwt(self.jwt_secret)

    async def _create_refresh_token(self, user: User) -> str:
        refresh_token = str(uuid.uuid4())
        await self.set_refresh_token(user_id=str(user.id), refresh_token=refresh_token)
        return refresh_token

    @token_error_handler
    @request_error_handler
    async def get(self, request):
        user_info: UserClaim = get_bearer_token(self.jwt_secret, request)
        return json_response(result=object_to_dict(user_info))

    @request_error_handler
    async def create_email_user_token(self, request):
        request_body: CreateEmailUserTokenRequest = convert_request(
            CreateEmailUserTokenRequest, await request.json())
        user: User = await find_user_by_account(request_body.account)

        if user is None:
            return json_response(reason='user not found', status=404)

        if not bcrypt.checkpw(request_body.password.encode(), user.hashed_password.encode()):
            return json_response(reason='Invalid password', status=403)

        refresh_token = await self._create_refresh_token(user)
        access_token = self._create_access_token(user)

        return json_response(result={
            'access_token': access_token,
            'refresh_token': refresh_token,
        })

    @request_error_handler
    async def create_third_party_user_token(self, request):
        request_body: CreateThirdPartyUserTokenRequest = convert_request(
            CreateThirdPartyUserTokenRequest, await request.json())
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

        if user is None:
            return json_response(reason='user not found', status=404)

        refresh_token = await self._create_refresh_token(user)
        access_token = self._create_access_token(user)

        return json_response(result={
            'access_token': access_token,
            'refresh_token': refresh_token,
        })

    @token_error_handler
    @request_error_handler
    async def put(self, request):
        request_body: RefreshTokenRequest = convert_request(
            RefreshTokenRequest, await request.json())

        user_id = await self.get_user_id_by_refresh_token(request_body.refresh_token)
        if user_id is None:
            return json_response(reason='token not found', status=404)

        user = await find_user_by_id(to_string(user_id))
        if not user:
            return json_response(
                reason=f'user not found', status=404)

        access_token = self._create_access_token(user)
        return json_response(result={
            'access_token': access_token
        })
