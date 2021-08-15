from typing import Dict

import aiohttp_cors

from aiohttp import web

from endpoint_test.jauth.external.callback.dummy import DummyCallbackHandler
from endpoint_test.jauth.external.token.dummy import DummyThirdPartyRequest
from jauth.config import config
from jauth.external.callback.user_create import UserCreationCallbackHandler
from jauth.external.callback.user_update import UserUpdateCallbackHandler
from jauth.external.token.apple import AppleToken
from jauth.external.token.facebook import FacebookToken
from jauth.external.token.google import GoogleToken
from jauth.external.token.kakao import KakaoToken
from jauth.model.token import Token
from jauth.model.user import UserType, User
from jauth.repository.token import TokenRepositoryImpl
from jauth.repository.user import UserRepositoryImpl
from jauth.resource import json_response
from jauth.resource.base import BaseResource
from jauth.resource.internal import InternalHttpResource
from jauth.resource.token import TokenHttpResource
from jauth.resource.users import UsersHttpResource
from jauth.util.logger.logger import get_logger
from jauth.util.tortoise import init_db
from jauth.util.util import object_to_dict


def plugin_app(app, prefix, nested, keys=()):
    for key in keys:
        nested[key] = app[key]
    app.add_subapp(prefix, nested)


async def application():
    logger = get_logger(__name__)

    app = web.Application(logger=logger)
    logger.debug(object_to_dict(config))
    mysql_config = config.api_server.mysql

    await init_db(
        host=mysql_config.host,
        port=mysql_config.port,
        user=mysql_config.user,
        password=mysql_config.password,
        db=mysql_config.database
    )
    user_repository = UserRepositoryImpl()
    token_repository = TokenRepositoryImpl()
    external = {
        'third_party': {
            'facebook': DummyThirdPartyRequest({
                'dummy-facebook-token': 'dummy-facebook-user-id',
                'dummy-facebook-token-dup': 'dummy-facebook-user-id',
            }, UserType.FACEBOOK),
            'kakao': DummyThirdPartyRequest({
                'dummy-kakao-token': 'dummy-kakao-user-id',
                'dummy-kakao-token-dup': 'dummy-kakao-user-id',
            }, UserType.KAKAO),
            'apple': DummyThirdPartyRequest({
                'dummy-apple-token': 'dummy-apple-user-id',
                'dummy-apple-token-dup': 'dummy-apple-user-id',
            }, UserType.APPLE),
            'google': DummyThirdPartyRequest({
                'dummy-google-token': 'dummy-google-user-id',
                'dummy-google-token-dup': 'dummy-google-user-id',
            }, UserType.GOOGLE),
        },
    }
    secret = {
        'jwt_secret': config.api_server.jwt_secret,
        'internal_api_keys': config.api_server.internal_api_keys,
    }
    user_creation_callback_handler = DummyCallbackHandler()
    user_update_callback_handler = DummyCallbackHandler()

    resource_list: Dict[str, BaseResource] = {
        '/users': UsersHttpResource(
            user_creation_callback_handler=user_creation_callback_handler,
            user_update_callback_handler=user_update_callback_handler,
            user_repository=user_repository,
            secret=secret,
            external=external,
        ),
        '/token': TokenHttpResource(
            user_repository=user_repository,
            token_repository=token_repository,
            secret=secret,
            external=external,
        ),
        '/internal': InternalHttpResource(
            user_repository=user_repository,
            secret=secret,
        ),
    }

    async def cleanup(request):
        await User.all().delete()
        await Token.all().delete()
        return json_response(result={'status': 'done'})

    app.router.add_get('/storage/clean-up', cleanup)

    for path, resource in resource_list.items():
        subapp = web.Application(logger=logger)
        resource.route(subapp.router)
        plugin_app(app, path, subapp)

    cors = aiohttp_cors.setup(app)
    allow_url = '*'

    for route in list(app.router.routes()):
        cors.add(
            route,
            {
                allow_url: aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    allow_headers='*',
                    allow_methods=[route.method]
                )
            }
        )

    return app
