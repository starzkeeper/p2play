from backend.application.common.exception import ApplicationException


class EntityDoesNotExistError(ApplicationException):
    pass


class OptimisticLockException(ApplicationException):
    pass


class TooManyRetries(ApplicationException):
    pass
