from backend.domain.common.exceptions import DomainException


class FriendRequestException(DomainException):
    pass


class FriendshipAlreadyExists(DomainException):
    pass
