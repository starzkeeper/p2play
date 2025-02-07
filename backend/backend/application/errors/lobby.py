from backend.application.common.exception import ApplicationException


class UserNotInLobby(ApplicationException):
    pass


class LobbyDoesNotExist(ApplicationException):
    pass
