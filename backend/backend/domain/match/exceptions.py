from backend.domain.common.exceptions import DomainException


class UserNotInMatch(DomainException):
    pass

class ActionIsNotAllowed(DomainException):
    pass