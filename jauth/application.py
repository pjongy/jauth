from typing import Dict

import aiohttp_cors

from aiohttp import web

from jauth.config import config
from jauth.external.callback.user_create import UserCreationCallbackHandler
from jauth.external.callback.user_update import UserUpdateCallbackHandler
from jauth.external.token.apple import AppleToken
from jauth.external.token.facebook import FacebookToken
from jauth.external.token.google import GoogleToken
from jauth.external.token.kakao import KakaoToken
from jauth.repository.token import TokenRepositoryImpl
from jauth.repository.user import UserRepositoryImpl
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
        db=mysql_config.database,
    )
    user_repository = UserRepositoryImpl()
    token_repository = TokenRepositoryImpl()
    external = {
        "third_party": {
            "facebook": FacebookToken(),
            "kakao": KakaoToken(),
            "apple": AppleToken(),
            "google": GoogleToken(),
        },
    }
    secret = {
        "jwt_secret": config.api_server.jwt_secret,
        "internal_api_keys": config.api_server.internal_api_keys,
    }
    user_creation_callback_handler = UserCreationCallbackHandler(
        config.api_server.event_callback_urls
    )
    user_update_callback_handler = UserUpdateCallbackHandler(
        config.api_server.event_callback_urls
    )

    resource_list: Dict[str, BaseResource] = {
        "/users": UsersHttpResource(
            user_creation_callback_handler=user_creation_callback_handler,
            user_update_callback_handler=user_update_callback_handler,
            user_repository=user_repository,
            secret=secret,
            external=external,
        ),
        "/token": TokenHttpResource(
            user_repository=user_repository,
            token_repository=token_repository,
            secret=secret,
            external=external,
        ),
        "/internal": InternalHttpResource(
            user_repository=user_repository,
            secret=secret,
        ),
    }

    for path, resource in resource_list.items():
        subapp = web.Application(logger=logger)
        resource.route(subapp.router)
        plugin_app(app, path, subapp)

    cors = aiohttp_cors.setup(app)
    allow_url = "*"

    for route in list(app.router.routes()):
        cors.add(
            route,
            {
                allow_url: aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    allow_headers="*",
                    allow_methods=[route.method],
                )
            },
        )

    return app
