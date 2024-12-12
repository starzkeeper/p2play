import enum

from pydantic import BaseModel

from schemas.common_schema import MessageAction, ChannelTypes, Message


class LobbyStatus(str, enum.Enum):
    WAITING = "waiting"
    SEARCHING = "searching"
    ACCEPTANCE = "acceptance"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class LobbyMessage(Message):
    action: MessageAction = MessageAction.MESSAGE_LOBBY
    type: ChannelTypes = ChannelTypes.LOBBY


class JoinMessage(Message):
    action: MessageAction = MessageAction.JOIN_LOBBY
    type: ChannelTypes = ChannelTypes.LOBBY


class LeaveMessage(Message):
    action: MessageAction = MessageAction.LEAVE_LOBBY
    type: ChannelTypes = ChannelTypes.LOBBY


class WaitAcceptanceMatchMessage(Message):
    action: MessageAction.ACCEPT_MATCH = MessageAction.ACCEPT_MATCH
    type: ChannelTypes = ChannelTypes.USER


class Lobby(BaseModel):
    owner_id: int
    players: str
    lobby_status: LobbyStatus = LobbyStatus.WAITING


class AcceptanceMatch(BaseModel):
    match_id: str
    lobby_id_1: str
    lobby_id_2: str
