import asyncio
from dataclasses import dataclass

from backend.application.common.interactor import Interactor
from backend.application.lobby.gateway import LobbyReader
from backend.application.match.gateway import MatchSaver, MatchReader, MatchPubSubInterface
from backend.domain.lobby.models import MatchId
from backend.domain.match.models import Match


@dataclass
class CreateMatchInputDTO:
    acceptance_id: MatchId


class CreateMatch(Interactor[CreateMatchInputDTO, None]):
    def __init__(
            self,
            match_reader: MatchReader,
            lobby_reader: LobbyReader,
            match_saver: MatchSaver,
            match_pubsub: MatchPubSubInterface
    ):
        self.match_reader = match_reader
        self.lobby_reader = lobby_reader
        self.match_saver = match_saver
        self.match_pubsub = match_pubsub

    async def __call__(self, data: CreateMatchInputDTO) -> None:
        all_ready: bool = await self.match_reader.check_all_ready(data.acceptance_id)
        if not all_ready:
            return

        lobby_id_1, lobby_id_2 = await self.match_reader.get_acceptance_meta(data.acceptance_id)
        (lobby_1, _), (lobby_2, _) = await asyncio.gather(
            self.lobby_reader.get_lobby(lobby_id_1),
            self.lobby_reader.get_lobby(lobby_id_2),
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
        await self.match_saver.create_match(match_data)

        await self.match_pubsub.publish_match_preparation_started(match_data.match_id)
