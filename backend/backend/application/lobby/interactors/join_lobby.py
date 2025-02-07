import asyncio
import logging
from dataclasses import dataclass

from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.errors.exceptions import OptimisticLockException, TooManyRetries
from backend.application.errors.lobby import LobbyDoesNotExist
from backend.application.lobby.actions import remove_player_action
from backend.application.lobby.gateway import LobbyReader, LobbySaver, QueueSaver, LobbyPubSubInterface
from backend.application.users.gateway import UserPubSubInterface
from backend.domain.lobby.exceptions import UserAlreadyInLobby
from backend.domain.lobby.models import LobbyId
from backend.domain.lobby.service import can_add_player_to_lobby
from backend.domain.user.models import User

logger = logging.getLogger('p2play')


@dataclass
class JoinLobbyDTO:
    lobby_id: LobbyId


class JoinLobby(Interactor[JoinLobbyDTO, None]):
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

    async def __call__(self, data: JoinLobbyDTO) -> None:
        user: User = await self.id_provider.get_current_user()
        lobby = await self.lobby_reader.lobby_exists(data.lobby_id)
        if not lobby:
            raise LobbyDoesNotExist

        previous_lobby_id = await self.lobby_reader.get_user_lobby_id(user.id)
        if previous_lobby_id == data.lobby_id:
            raise UserAlreadyInLobby

        if previous_lobby_id:
            await remove_player_action(
                self.lobby_saver,
                self.lobby_reader,
                previous_lobby_id,
                user.id,
                self.queue_saver,
                self.lobby_pubsub,
                self.user_pubsub,
            )

        max_retries = 5
        for attempt in range(max_retries):
            try:
                lobby, version = await self.lobby_reader.get_lobby(data.lobby_id)
                if not lobby:
                    raise LobbyDoesNotExist

                can_add_player_to_lobby(lobby, user.id)
                await self.lobby_saver.add_player_to_lobby(lobby.lobby_id, user.id, version)
                await self.lobby_saver.set_player_lobby(lobby.lobby_id, user.id)

                await self.user_pubsub.publish_user_joined_message(user_id=user.id, lobby_id=lobby.lobby_id)
                await self.lobby_pubsub.publish_user_joined_message(user_id=user.id, lobby_id=lobby.lobby_id)
                break
            except OptimisticLockException:
                if attempt == max_retries - 1:
                    raise TooManyRetries
                await asyncio.sleep(0.01)
                continue
