class TokenError(Exception):
    message = 'unknown token error'

    def __init__(self, *args):
        if not args:
            args = (self.message,)

        super().__init__(*args)


class TokenExpiredException(TokenError):
    message = 'token expired'


class InvalidTokenException(TokenError):
    message = 'invalid token'


class TokenNotDeliveredError(TokenError):
    message = 'token is not delivered'
