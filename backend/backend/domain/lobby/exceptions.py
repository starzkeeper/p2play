from backend.domain.common.exceptions import DomainException


class UserNotInLobbyException(DomainException):
    pass


class UserInMatch(DomainException):
    pass


class UserAlreadyInLobby(DomainException):
    pass


class LobbyIsFull(DomainException):
    pass


class UserIsNotOwner(DomainException):
    pass


class LobbyAlreadyInMatch(DomainException):
    pass
