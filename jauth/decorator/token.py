import functools
import json

from aiohttp import web

from jauth.exception.token import TokenError


def token_error_handler(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TokenError as e:
            error_msg = e.message

        return web.Response(
            body=json.dumps({
                'success': False,
                'result': '',
                'reason': error_msg,
            }),
            content_type='application/json',
            status=401,
        )
    return wrapper
