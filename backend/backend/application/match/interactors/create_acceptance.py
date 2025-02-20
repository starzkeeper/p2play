import asyncio
import json
import uuid
from dataclasses import dataclass

from backend.application.common.interactor import Interactor
from backend.application.lobby.gateway import LobbySaver, LobbyReader
from backend.application.match.gateway import MatchPubSubInterface, MatchSaver
from backend.application.queue.gateway import QueueReader, QueueSaver
from backend.domain.lobby.models import LobbyStatus, LobbyId


@dataclass
class CreateAcceptanceInputDTO:
    lobby_id_1: LobbyId
    lobby_id_2: LobbyId


class CreateAcceptance(Interactor[None, None]):
    def __init__(
            self,
            match_saver: MatchSaver,
            lobby_saver: LobbySaver,
            lobby_reader: LobbyReader,
            queue_reader: QueueReader,
            queue_saver: QueueSaver,
            match_pubsub: MatchPubSubInterface
    ):
        self.match_saver = match_saver
        self.lobby_saver = lobby_saver
        self.lobby_reader = lobby_reader
        self.queue_reader = queue_reader
        self.queue_saver = queue_saver
        self.match_pubsub = match_pubsub

    async def __call__(self, data: None = None) -> None:  # TODO: algorithm
        queue: int = await self.queue_reader.get_queue_len()
        if queue < 2:
            return

        lobby_id_1, lobby_id_2 = asyncio.gather(
            self.queue_saver.take_id_from_queue(),
            self.queue_saver.take_id_from_queue()
        )

        (lobby_1, version_1), (lobby_2, version_2) = await asyncio.gather(
            self.lobby_reader.get_lobby(lobby_id_1),
            self.lobby_reader.get_lobby(lobby_id_2),
        )

        lobby_1.lobby_status = LobbyStatus.ACCEPTANCE
        lobby_2.lobby_status = LobbyStatus.ACCEPTANCE

        match_id = str(uuid.uuid4())
        lobby_1.match_id = match_id
        lobby_2.match_id = match_id
        await asyncio.gather(
            self.lobby_saver.update_lobby(lobby_1, version_1),
            self.lobby_saver.update_lobby(lobby_2, version_2)
        )

        all_players: list[int] = lobby_1.players + lobby_2.players
        acceptance: dict[str, bool] = {str(player_id): json.dumps(False) for player_id in all_players}

        await asyncio.gather(
            self.match_saver.create_acceptance_meta(match_id, lobby_id_1, lobby_id_2),
            self.match_saver.create_acceptance(match_id, acceptance)
        )

        await asyncio.gather(
            self.match_pubsub.publish_lobby_match_found(lobby_id_1, match_id),
            self.match_pubsub.publish_lobby_match_found(lobby_id_2, match_id)
        )
