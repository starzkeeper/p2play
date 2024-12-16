import enum

from pydantic import BaseModel, field_validator

from backend.schemas.common_schema import Message, ChannelTypes, BaseEnum


class LobbyStatus(str, BaseEnum):
    WAITING = "waiting"
    SEARCHING = "searching"
    ACCEPTANCE = "acceptance"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class UserAction(str, BaseEnum):
    # Redis
    JOIN_LOBBY = "join_lobby"
    LEAVE_LOBBY = "leave_lobby"


class LobbyAction(str, BaseEnum):
    START_SEARCH = 'start_search'
    STOP_SEARCH = 'stop_search'
    USER_JOINED_MESSAGE = 'user_joined'
    USER_LEFT_MESSAGE = 'user_left'

    # Redis
    ACCEPT_MATCH = 'accept_match'


class AcceptanceAction(str, BaseEnum):
    USER_ACCEPTED = 'user_accepted'

    # REDIS
    JOIN_MATCH = 'join_match'


class UserMessage(Message):
    user_id: int | str
    type: ChannelTypes = ChannelTypes.USER
    lobby_id: str | None = None

    @field_validator('lobby_id')
    @classmethod
    def validate_lobby_id(cls, value, values):
        action = values.get('action')
        if (action == UserAction.JOIN_LOBBY or action == UserAction.LEAVE_LOBBY) and value is None:
            raise ValueError("lobby_id is required")
        return value


class LobbyMessage(Message):
    type: ChannelTypes = ChannelTypes.LOBBY
    from_lobby_id: str
    acceptance_id: str | None = None
    user_id: int | str | None = None

    @field_validator('acceptance_id')
    @classmethod
    def validate_lobby_id(cls, value, values):
        action = values.get('action')
        if action == LobbyAction.ACCEPT_MATCH and value is None:
            raise ValueError("acceptance_id is required")
        return value

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, value, values):
        action = values.get('action')
        if action == LobbyAction.USER_JOINED_MESSAGE or action == LobbyAction.USER_LEFT_MESSAGE and value is None:
            raise ValueError("user_id is required")
        return value


class AcceptanceMessage(Message):
    type: ChannelTypes = ChannelTypes.ACCEPTANCE
    user_id: int | str | None = None
    match_id: str

    @field_validator('user_id')
    @classmethod
    def validate_lobby_id(cls, value, values):
        action = values.get('action')
        if action == AcceptanceAction.USER_ACCEPTED and value is None:
            raise ValueError("user_id is required")
        return value


class Lobby(BaseModel):
    owner_id: int
    players: str
    lobby_status: LobbyStatus = LobbyStatus.WAITING


class AcceptanceMatch(BaseModel):
    match_id: str
    lobby_id_1: str
    lobby_id_2: str
