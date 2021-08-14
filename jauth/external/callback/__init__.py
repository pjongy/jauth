from aiohttp import ClientSession
from pydantic import BaseModel


class BaseCallbackMessage(BaseModel):
    issuer: str = 'jauth'
    token: str
    type: str
    issued_at: int


async def post_json(session: ClientSession, url: str, body: dict, header=None) -> dict:
    if header is None:
        header = {}
    async with session.post(url=url, json=body, headers=header) as response:
        return await response.json()
