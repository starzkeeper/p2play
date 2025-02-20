import logging

from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.lobby.actions import remove_player_action
from backend.application.lobby.gateway import LobbyReader, LobbySaver, LobbyPubSubInterface
from backend.application.queue.gateway import QueueSaver
from backend.application.users.gateway import UserPubSubInterface
from backend.domain.lobby.models import LobbyId, Lobby
from backend.domain.user.models import User

logger = logging.getLogger('p2play')


class CreateLobby(Interactor[None, LobbyId]):
    def __init__(
            self,
            lobby_reader: LobbyReader,
            lobby_saver: LobbySaver,
            queue_saver: QueueSaver,
            id_provider: IdProvider,
            lobby_pubsub: LobbyPubSubInterface,
            user_pubsub: UserPubSubInterface,
    ):
        self.lobby_reader = lobby_reader
        self.lobby_saver = lobby_saver
        self.queue_saver = queue_saver
        self.id_provider = id_provider
        self.lobby_pubsub = lobby_pubsub
        self.user_pubsub = user_pubsub

    async def __call__(self, data: None = None) -> LobbyId:
        user: User = await self.id_provider.get_current_user()
        previous_lobby_id = await self.lobby_reader.get_user_lobby_id(user.id)
        if previous_lobby_id:
            logger.debug('Lobby exist')
            await remove_player_action(
                self.lobby_saver,
                self.lobby_reader,
                previous_lobby_id,
                user.id,
                self.queue_saver,
                self.lobby_pubsub,
                self.user_pubsub,
            )

        lobby = Lobby(
            owner_id=user.id,
            players=[user.id]
        )
        await self.lobby_saver.create_lobby(lobby)
        await self.lobby_saver.set_player_lobby(lobby.lobby_id, user.id)

        await self.user_pubsub.publish_user_joined_message(user_id=user.id, lobby_id=lobby.lobby_id)
        await self.lobby_pubsub.publish_user_joined_message(user_id=user.id, lobby_id=lobby.lobby_id)
        return LobbyId(lobby.lobby_id)
