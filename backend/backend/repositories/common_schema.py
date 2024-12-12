import enum
import time

from pydantic import BaseModel, Field


class MessageAction(str, enum.Enum):
    JOIN_LOBBY = 'join_lobby'
    LEAVE_LOBBY = 'leave_lobby'
    MESSAGE_LOBBY = 'message_lobby'

    JOIN_MATCH = 'join_match'
    LEAVE_MATCH = 'leave_match'
    ACCEPT_MATCH = 'accept_match'
    MESSAGE_MATCH = 'message_match'


class ChannelTypes(str, enum.Enum):
    LOBBY = 'lobby'
    MATCH = 'match'
    USER = 'user'


class Message(BaseModel):
    user_id: int | str
    action: MessageAction
    message: str | None
    timestamp: int = Field(default_factory=lambda: int(time.time()))
