from dataclasses import dataclass

from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.domain.lobby.models import LobbyId, UserLobbyAction
from backend.domain.user.models import UserId


@dataclass
class ChatLobbyMessageInputDTO:
    message: str


@dataclass
class ChatLobbyMessageOutputDTO:
    message: str
    lobby_id: LobbyId
    user_id: UserId
    action: UserLobbyAction = UserLobbyAction.MESSAGE_LOBBY


class SendChatLobbyMessage(Interactor[ChatLobbyMessageInputDTO, None]):
    def __init__(
            self,
            id_provider: IdProvider
    ):
        self.id_provider = id_provider

    async def __call__(self, data: None = None) -> None:
        user = await self.id_provider.get_current_user()
        print(user.id)
