import enum
import time

from pydantic import BaseModel, Field


class MessageAction(str, enum.Enum):
    JOIN = 'join'
    LEAVE = 'leave'
    MESSAGE = 'message'
    ACCEPT_MATCH = 'accept_match'


class ChannelTypes(str, enum.Enum):
    LOBBY = 'lobby'
    MATCH = 'match'


class Message(BaseModel):
    user_id: int | str
    action: MessageAction
    message: str | None
    timestamp: int = Field(default_factory=lambda: int(time.time()))
