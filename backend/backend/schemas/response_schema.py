from enum import Enum
from typing import Union, Dict, Any, TypedDict


class ApiStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class DefaultApiResponse(TypedDict):
    status: ApiStatus
    message: Union[list[Dict[str, Any]], str] | Dict
