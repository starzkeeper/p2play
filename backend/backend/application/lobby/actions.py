import asyncio
import json
import logging
import uuid

from backend.application.errors.exceptions import OptimisticLockException, TooManyRetries
from backend.application.errors.lobby import LobbyDoesNotExist
from backend.application.lobby.gateway import LobbySaver, LobbyReader, QueueSaver, QueueReader, LobbyPubSubInterface
from backend.application.match.gateway import MatchSaver
from backend.application.users.gateway import UserPubSubInterface
from backend.domain.lobby.exceptions import LobbyAlreadyInMatch
from backend.domain.lobby.models import LobbyId, LobbyStatus
from backend.domain.lobby.service import check_user_in_players, remove_player_from_lobby
from backend.domain.match.models import Match
from backend.domain.user.models import UserId

logger = logging.getLogger('p2play')


async def remove_player_action(
        lobby_saver: LobbySaver,
        lobby_reader: LobbyReader,
        lobby_id: LobbyId,
        user_id: UserId,
        queue_saver: QueueSaver,
        lobby_pubsub: LobbyPubSubInterface,
        user_pubsub: UserPubSubInterface,
):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            lobby, version = await lobby_reader.get_lobby(lobby_id)
            if lobby.lobby_status not in (LobbyStatus.SEARCHING, LobbyStatus.WAITING):
                raise LobbyAlreadyInMatch

            check_user_in_players(user_id, lobby.players)

            if len(lobby.players) == 1:
                await lobby_saver.delete_lobby(lobby_id, version)
                logger.debug('lobby deleted')
                await lobby_saver.clear_user_lobby(user_id)
                await user_pubsub.publish_user_left_message(user_id=user_id, lobby_id=lobby_id)
                return

            updated_lobby = remove_player_from_lobby(lobby, user_id)
            await lobby_saver.update_lobby(
                updated_lobby, version
            )

            if lobby.lobby_status == LobbyStatus.SEARCHING:
                await queue_saver.remove_from_queue(lobby_id)  # ВРЕМЕННОЕ РЕШЕНИЕ
                await lobby_pubsub.publish_lobby_stop_searching(lobby_id)

            await lobby_saver.clear_user_lobby(user_id)

            await user_pubsub.publish_user_left_message(user_id=user_id, lobby_id=lobby_id)
            await lobby_pubsub.publish_user_left_message(user_id=user_id, lobby_id=lobby.lobby_id)
            break
        except OptimisticLockException:
            if attempt == max_retries - 1:
                raise TooManyRetries
            await asyncio.sleep(0.01)
            continue
        except LobbyDoesNotExist:
            break


async def start_acceptance(
        lobby_saver: LobbySaver,
        lobby_reader: LobbyReader,
        queue_reader: QueueReader,
        queue_saver: QueueSaver,
):  # ВРЕМЕННОЕ РЕШЕНИЕ
    queue: int = await queue_reader.get_queue_len()
    if queue < 2:
        return

    lobby_id_1 = await queue_saver.take_id_from_queue()
    lobby_id_2 = await queue_saver.take_id_from_queue()

    lobby_1, version = await lobby_reader.get_lobby(lobby_id_1)
    lobby_2, version_2 = await lobby_reader.get_lobby(lobby_id_2)

    lobby_1.lobby_status = LobbyStatus.ACCEPTANCE
    lobby_2.lobby_status = LobbyStatus.ACCEPTANCE
    match_id = str(uuid.uuid4())
    lobby_1.match_id = match_id
    lobby_2.match_id = match_id
    await lobby_saver.update_lobby(lobby_1, version)
    await lobby_saver.update_lobby(lobby_2, version_2)

    players_1: list = await lobby_reader.get_players(lobby_id_1)
    players_2: list = await lobby_reader.get_players(lobby_id_2)

    all_players: list[int] = players_1 + players_2
    acceptance: dict[str, bool] = {str(player_id): json.dumps(False) for player_id in all_players}

    await lobby_saver.create_acceptance_meta(match_id, lobby_id_1, lobby_id_2)
    await lobby_saver.create_acceptance(match_id, acceptance)
    # TODO: Send acceptance


async def start_match(
        lobby_reader: LobbyReader,
        match_saver: MatchSaver,
        acceptance_id: LobbyId,
):  # ВРЕМЕННОЕ РЕШЕНИЕ
    lobby_id_1, lobby_id_2 = await lobby_reader.get_acceptance_meta(acceptance_id)
    (lobby_1, _), (lobby_2, _) = await asyncio.gather(
        lobby_reader.get_lobby(lobby_id_1),
        lobby_reader.get_lobby(lobby_id_2),
    )

    match_data = Match(
        match_id=lobby_1.match_id,
        owner_team_1=lobby_1.owner_id,
        owner_team_2=lobby_2.owner_id,
        team_1=lobby_1.players,
        team_2=lobby_2.players,
        lobby_id_1=lobby_id_1,
        lobby_id_2=lobby_id_2,
    )
    await match_saver.create_match(match_data)
