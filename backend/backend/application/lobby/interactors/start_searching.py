from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.lobby.actions import start_acceptance
from backend.application.lobby.gateway import LobbyReader, LobbySaver, QueueSaver, QueueReader, LobbyPubSubInterface
from backend.domain.lobby.exceptions import LobbyAlreadyInMatch
from backend.domain.lobby.models import LobbyStatus
from backend.domain.lobby.service import check_user_is_owner


class StartSearching(Interactor[None, None]):
    def __init__(
            self,
            lobby_reader: LobbyReader,
            lobby_saver: LobbySaver,
            queue_saver: QueueSaver,
            queue_reader: QueueReader,
            lobby_pubsub: LobbyPubSubInterface,
            id_provider: IdProvider,
    ):
        self.lobby_reader = lobby_reader
        self.lobby_saver = lobby_saver
        self.queue_saver = queue_saver
        self.queue_reader = queue_reader
        self.lobby_pubsub = lobby_pubsub
        self.id_provider = id_provider

    async def __call__(self, data: None = None) -> None:
        user = await self.id_provider.get_current_user()
        lobby_id = await self.lobby_reader.get_user_lobby_id(user.id)  # TODO: From front

        lobby, version = await self.lobby_reader.get_lobby(lobby_id)
        check_user_is_owner(lobby.owner_id, user.id)

        if lobby.lobby_status != LobbyStatus.WAITING:
            raise LobbyAlreadyInMatch

        lobby.lobby_status = LobbyStatus.SEARCHING
        await self.lobby_saver.update_lobby(lobby, version)
        await self.queue_saver.add_to_queue(lobby_id)
        await self.lobby_pubsub.publish_lobby_start_searching(lobby_id)

        await start_acceptance(
            self.lobby_saver,
            self.lobby_reader,
            self.queue_reader,
            self.queue_saver,
        )
