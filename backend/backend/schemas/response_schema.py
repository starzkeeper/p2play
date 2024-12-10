from enum import Enum
from typing import Any, TypedDict


class ApiStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class DefaultApiResponse(TypedDict):
    status: ApiStatus
    message: Any
