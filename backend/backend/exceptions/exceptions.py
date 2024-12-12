from starlette import status


class BaseCustomException(Exception):
    def __init__(self, message: str | None = None, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code


class ServiceError(BaseCustomException):
    """Failures in external services or APIs."""
    def __init__(self):
        super().__init__("External service error", status_code=status.HTTP_424_FAILED_DEPENDENCY)


class EntityDoesNotExistError(BaseCustomException):
    """Database returns nothing."""
    def __init__(self, entity_name: str = "Entity"):
        super().__init__(f"{entity_name} does not exist", status_code=status.HTTP_404_NOT_FOUND)


class EntityAlreadyExistsError(BaseCustomException):
    """Conflict detected, like trying to create a resource that already exists."""
    def __init__(self, entity_name: str = "Entity"):
        super().__init__(f"{entity_name} already exists", status_code=status.HTTP_409_CONFLICT)


class InvalidOperationError(BaseCustomException):
    """Invalid operations like trying to delete a non-existing entity, etc."""
    def __init__(self):
        super().__init__(f"Invalid operation", status_code=status.HTTP_400_BAD_REQUEST)


class AuthenticationFailed(BaseCustomException):
    """Invalid authentication credentials."""
    def __init__(self):
        super().__init__("Authentication failed", status_code=status.HTTP_401_UNAUTHORIZED)


class InvalidTokenError(BaseCustomException):
    """Invalid token."""
    def __init__(self):
        super().__init__("Invalid token", status_code=status.HTTP_401_UNAUTHORIZED)