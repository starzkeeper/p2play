import enum
import time

from pydantic import BaseModel, Field


class LobbyStatus(str, enum.Enum):
    WAITING = "waiting"
    FULL = "full"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Sender(str, enum.Enum):
    USER_CHANNEL = "user_channel"
    LOBBY_CHANNEL = "lobby_channel"


class MessageAction(str, enum.Enum):
    JOIN = 'join'
    LEAVE = 'LEAVE'
    MESSAGE = 'message'


class UserMessage(BaseModel):
    user_id: int
    action: MessageAction
    message: str
    timestamp: int = Field(default_factory=lambda: int(time.time()))


class LobbyMessage(UserMessage):
    action: MessageAction = MessageAction.MESSAGE
    lobby_id: str


class JoinMessage(UserMessage):
    action: MessageAction = MessageAction.JOIN
    lobby_id: str
