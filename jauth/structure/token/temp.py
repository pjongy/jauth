import deserialize

from jauth.structure.token.jwt import JwtClaim


@deserialize.default('iss', 'jauth-temp-email')
@deserialize.parser('type', int)
class VerifyUserEmailClaim(JwtClaim):
    id: str
    type: int
    iss: str = 'jauth-temp-email'  # NOTE: for check issuer (class variable)
