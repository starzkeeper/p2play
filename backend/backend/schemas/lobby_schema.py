import enum

from pydantic import BaseModel

from backend.repositories.common_schema import MessageAction, ChannelTypes, Message


class LobbyStatus(str, enum.Enum):
    WAITING = "waiting"
    SEARCHING = "searching"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Recipient(str, enum.Enum):
    USER_CHANNEL = "user_channel"
    LOBBY_CHANNEL = "lobby_channel"
    MATCH_CHANNEL = "match_channel"


class LobbyMessage(Message):
    action: MessageAction = MessageAction.MESSAGE
    type: ChannelTypes = ChannelTypes.LOBBY
    lobby_id: str


class JoinMessage(Message):
    action: MessageAction = MessageAction.JOIN
    type: ChannelTypes = ChannelTypes.LOBBY
    lobby_id: str


class LeaveMessage(Message):
    action: MessageAction = MessageAction.LEAVE
    type: ChannelTypes = ChannelTypes.LOBBY
    lobby_id: str


class WaitAcceptanceMatchMessage(Message):
    action: MessageAction.ACCEPT_MATCH = MessageAction.ACCEPT_MATCH
    type: ChannelTypes = ChannelTypes.MATCH
    match_id: str


class Lobby(BaseModel):
    owner_id: int
    players: str
    lobby_status: LobbyStatus = LobbyStatus.WAITING
