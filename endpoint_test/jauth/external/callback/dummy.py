from jauth.external.callback.base import BaseCallbackHandler


class DummyCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__([('', '')])
        self.messages = []

    async def handle(self, message: dict) -> bool:
        self.messages.append(message)
        return True
