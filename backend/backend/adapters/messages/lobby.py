from backend.adapters.messages.message import Message, ChannelTypes
from backend.domain.lobby.models import LobbyId, MatchId
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
