from backend.domain.common.exceptions import DomainException


class AuthenticationError(DomainException):
    pass


class AccessDenied(DomainException):
    pass

class TokenNotExist(DomainException):
    pass
