import asyncio
import logging

from backend.application.errors.exceptions import OptimisticLockException, TooManyRetries
from backend.application.errors.lobby import LobbyDoesNotExist
from backend.application.lobby.gateway import LobbySaver, LobbyReader, LobbyPubSubInterface
from backend.application.lobby.services_interface import QueueServiceInterface
from backend.application.users.gateway import UserPubSubInterface
from backend.domain.lobby.exceptions import LobbyAlreadyInMatch
from backend.domain.lobby.models import LobbyId, LobbyStatus
from backend.domain.lobby.service import check_user_in_players, remove_player_from_lobby
from backend.domain.user.models import UserId

logger = logging.getLogger('p2play')


async def remove_player_action(
        lobby_saver: LobbySaver,
        lobby_reader: LobbyReader,
        lobby_id: LobbyId,
        user_id: UserId,
        lobby_pubsub: LobbyPubSubInterface,
        user_pubsub: UserPubSubInterface,
        queue_service: QueueServiceInterface,
):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            lobby, version = await lobby_reader.get_lobby(lobby_id)
            if lobby.lobby_status not in (LobbyStatus.SEARCHING, LobbyStatus.WAITING):
                raise LobbyAlreadyInMatch

            check_user_in_players(user_id, lobby.players)

            if lobby.lobby_status == LobbyStatus.SEARCHING:
                asyncio.gather(
                    queue_service.remove_from_queue(lobby_id),
                    lobby_pubsub.publish_lobby_stop_searching(lobby_id),
                )

            if len(lobby.players) == 1:
                await lobby_saver.delete_lobby(lobby_id, version)
                logger.debug('lobby deleted')
                asyncio.gather(
                    lobby_saver.clear_user_lobby(user_id),
                    user_pubsub.publish_user_left_message(user_id=user_id, lobby_id=lobby_id),
                )
                return

            updated_lobby = remove_player_from_lobby(lobby, user_id)
            await lobby_saver.update_lobby(
                updated_lobby, version
            )

            asyncio.gather(
                lobby_saver.clear_user_lobby(user_id),
                user_pubsub.publish_user_left_message(user_id=user_id, lobby_id=lobby_id),
                lobby_pubsub.publish_user_left_message(user_id=user_id, lobby_id=lobby.lobby_id),
            )
            break
        except OptimisticLockException:
            if attempt == max_retries - 1:
                raise TooManyRetries
            await asyncio.sleep(0.01)
            continue
        except LobbyDoesNotExist:
            break
