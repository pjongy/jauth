import aiohttp

DEFAULT_HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}
DEFAULT_HEADERS_FORM_DATA = {
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
}


async def post(url='', parameters=None, headers=None, is_json=True):
    if headers is None:
        headers = {}
    if parameters is None:
        parameters = {}
    if is_json:
        post_params = {'json': parameters}
        default_header = DEFAULT_HEADERS
    else:
        post_params = {'data': parameters}
        default_header = DEFAULT_HEADERS_FORM_DATA
    async with aiohttp.ClientSession(headers={**default_header, **headers}) as session:
        async with session.post(url, **post_params) as resp:
            return resp.status, await resp.json(), resp.headers
