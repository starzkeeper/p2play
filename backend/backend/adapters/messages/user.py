from backend.adapters.messages.message import Message, ChannelTypes
from backend.domain.lobby.models import LobbyId
from backend.domain.user.models import UserId


class UserMessage(Message):
    user_id: UserId
    type: ChannelTypes = ChannelTypes.USER
    lobby_id: LobbyId | None = None
