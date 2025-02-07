import time
from enum import auto

from pydantic import BaseModel, Field

from backend.domain.common.base_enum import BaseStrEnum


class ChannelTypes(BaseStrEnum):
    LOBBY = auto()
    MATCH = auto()
    USER = auto()
    ACCEPTANCE = auto()


class Message(BaseModel):
    action: BaseStrEnum
    message: str | None
    type: ChannelTypes
    timestamp: int = Field(default_factory=lambda: int(time.time()))
