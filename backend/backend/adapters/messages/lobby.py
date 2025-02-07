from pydantic import field_validator
from pydantic_core.core_schema import FieldValidationInfo

from backend.adapters.messages.message import Message, ChannelTypes
from backend.domain.lobby.models import AcceptanceAction, LobbyId, MatchId
from backend.domain.user.models import UserId


class LobbyMessage(Message):
    type: ChannelTypes = ChannelTypes.LOBBY
    from_lobby_id: LobbyId
    match_id: MatchId | None = None
    user_id: UserId | None = None


class AcceptanceMessage(Message):
    type: ChannelTypes = ChannelTypes.ACCEPTANCE
    user_id: UserId | None = None
    match_id: MatchId

    @field_validator('user_id')
    @classmethod
    def validate_lobby_id(cls, value, info: FieldValidationInfo):
        action = info.data.get('action')
        if action == AcceptanceAction.USER_ACCEPTED and value is None:
            raise ValueError("user_id is required")
        return value
