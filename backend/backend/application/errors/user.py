from backend.application.common.exception import ApplicationException


class UserAlreadyExists(ApplicationException):
    pass


class AuthenticationFailed(ApplicationException):
    pass


class UserNotFound(ApplicationException):
    pass


class UserAlreadyLogged(ApplicationException):
    pass
