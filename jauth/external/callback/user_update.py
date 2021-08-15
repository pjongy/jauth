import asyncio
from typing import List, Tuple, Optional

from aiohttp import ClientSession

from jauth.external.callback import BaseCallbackMessage, post_json
from jauth.external.callback.base import BaseCallbackHandler
from jauth.util.logger.logger import get_logger
from jauth.util.util import utc_now

logger = get_logger(__name__)


class UserUpdateCallbackMessage(BaseCallbackMessage):
    user__id: str
    user__email: Optional[str]
    user__status: str
    user__is_email_verified: bool
    user__extra: dict


class UserUpdateCallbackHandler(BaseCallbackHandler):
    def __init__(self, urls: List[Tuple[str, str]]):
        # Tuple[str, str] : (URL, TOKEN)
        super().__init__(urls)

    async def handle(self, message: dict) -> bool:
        user_id = str(message["id"])
        logger.info(f"Generate user deletion event with {user_id}")
        async with ClientSession() as session:
            await asyncio.gather(
                *[
                    post_json(
                        session=session,
                        url=url[0],
                        body=UserUpdateCallbackMessage(
                            type="jauth.user.update",
                            issued_at=utc_now().timestamp(),
                            token=url[1],
                            user__id=user_id,
                            user__email=message["email"],
                            user__status=message["status"],
                            user__is_email_verified=message["is_email_verified"],
                            user__extra=message["extra"],
                        ).dict(),
                    )
                    for url in self.urls
                ],
                return_exceptions=True,
            )
        return True
