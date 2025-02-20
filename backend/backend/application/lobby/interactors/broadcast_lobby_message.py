from dataclasses import dataclass

from backend.application.common.interactor import Interactor
from backend.application.lobby.gateway import LobbyReader, LobbyPubSubInterface
from backend.domain.user.models import UserId


@dataclass
class BroadcastLobbyMessageInputDTO:
    user_id: UserId
    message: str


class BroadcastLobbyMessage(Interactor[BroadcastLobbyMessageInputDTO, None]):
    def __init__(
            self,
            lobby_reader: LobbyReader,
            lobby_pubsub: LobbyPubSubInterface
    ):
        self.lobby_reader = lobby_reader
        self.lobby_pubsub = lobby_pubsub

    async def __call__(self, data: BroadcastLobbyMessageInputDTO) -> None:
        lobby_id = await self.lobby_reader.get_user_lobby_id(data.user_id)
        await self.lobby_pubsub.publish_lobby_user_message(data.user_id, lobby_id, data.message)
