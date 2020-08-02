import aiohttp_cors

import aioredis
from aiohttp import web
from aioredis import ConnectionsPool

from apiserver.config import config
from apiserver.external.token.apple import AppleToken
from apiserver.external.token.facebook import FacebookToken
from apiserver.external.token.kakao import KakaoToken
from apiserver.resource.token import TokenHttpResource
from apiserver.resource.users import UsersHttpResource
from common.logger.logger import get_logger
from common.storage.init import init_db


def plugin_app(app, prefix, nested, keys=()):
    for key in keys:
        nested[key] = app[key]
    app.add_subapp(prefix, nested)


async def application():
    logger = get_logger(__name__)

    app = web.Application(logger=logger)
    mysql_config = config.api_server.mysql
    await init_db(
        host=mysql_config.host,
        port=mysql_config.port,
        user=mysql_config.user,
        password=mysql_config.password,
        db=mysql_config.database,
    )

    redis_config = config.api_server.redis

    token_cache: ConnectionsPool = await aioredis.create_pool(
        f'redis://{redis_config.host}:{redis_config.port}',
        password=redis_config.password,
        minsize=5,
        maxsize=10,
        db=redis_config.token_cache.database,
    )

    storage = {
        'redis': {
            'token_cache': token_cache,
        }
    }
    external = {
        'third_party': {
            'facebook': FacebookToken(),
            'kakao': KakaoToken(),
            'apple': AppleToken(),
        },
    }
    secret = {
        'jwt_secret': config.api_server.jwt_secret,
    }
    resource_list = {
        '/users': UsersHttpResource,
        '/token': TokenHttpResource,
    }

    for path, resource in resource_list.items():
        subapp = web.Application(logger=logger)
        resource(
            router=subapp.router,
            storage=storage,
            secret=secret,
            external=external,
        ).route()
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
