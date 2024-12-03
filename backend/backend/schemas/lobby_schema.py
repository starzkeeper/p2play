import enum
import time
from typing import TypedDict

from pydantic import BaseModel, Field


class LobbyStatus(str, enum.Enum):
    WAITING = "waiting"
    FULL = "full"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class MessageAction(str, enum.Enum):
    JOIN = 'join'
    LEAVE = 'LEAVE'
    MESSAGE = 'message'


class LobbyMessage(BaseModel):
    user_id: int
    action: MessageAction = MessageAction.MESSAGE
    message: str
    timestamp: int = Field(default_factory=lambda: int(time.time()))


class JoinMessage(BaseModel):
    action: MessageAction = MessageAction.JOIN
    lobby_id: str
    message: str
    timestamp: int = Field(default_factory=lambda: int(time.time()))

