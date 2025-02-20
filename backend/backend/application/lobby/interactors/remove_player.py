from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.errors.lobby import UserNotInLobby
from backend.application.lobby.actions import remove_player_action
from backend.application.lobby.gateway import LobbySaver, LobbyReader, LobbyPubSubInterface
from backend.application.lobby.services_interface import QueueServiceInterface
from backend.application.users.gateway import UserPubSubInterface
from backend.domain.user.models import User


class RemovePlayer(Interactor[None, None]):
    def __init__(
            self,
            lobby_saver: LobbySaver,
            lobby_reader: LobbyReader,
            queue_service: QueueServiceInterface,
            id_provider: IdProvider,
            lobby_pubsub: LobbyPubSubInterface,
            user_pubsub: UserPubSubInterface
    ):
        self.lobby_saver = lobby_saver
        self.lobby_reader = lobby_reader
        self.queue_service = queue_service
        self.id_provider = id_provider
        self.lobby_pubsub = lobby_pubsub
        self.user_pubsub = user_pubsub

    async def __call__(self, data: None = None) -> None:
        user: User = await self.id_provider.get_current_user()
        lobby_id = await self.lobby_reader.get_user_lobby_id(user.id)
        if not lobby_id:
            raise UserNotInLobby

        await remove_player_action(
            self.lobby_saver,
            self.lobby_reader,
            lobby_id,
            user.id,
            self.lobby_pubsub,
            self.user_pubsub,
            self.queue_service
        )
