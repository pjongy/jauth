import deserialize

from jauth.structure.token.jwt import JwtClaim


@deserialize.default('iss', 'jauth-temp-email')
@deserialize.parser('type', int)
class VerifyUserEmailClaim(JwtClaim):
    id: str
    type: int
    iss: str = 'jauth-temp-email'  # NOTE: for check issuer (class variable)


@deserialize.default('iss', 'jauth-temp-password-reset')
@deserialize.parser('type', int)
class ResetPasswordClaim(JwtClaim):
    id: str
    type: int
    iss: str = 'jauth-temp-password-reset'  # NOTE: for check issuer (class variable)
