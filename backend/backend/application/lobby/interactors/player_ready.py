import logging
from dataclasses import dataclass

from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.lobby.actions import start_match
from backend.application.lobby.gateway import LobbySaver, LobbyReader
from backend.application.match.gateway import MatchSaver
from backend.domain.match.models import MatchId, Match

logger = logging.getLogger('p2play')


@dataclass
class PlayerReadyDTO:
    acceptance_id: MatchId


class PlayerReady(Interactor[PlayerReadyDTO, None]):
    def __init__(
            self,
            lobby_saver: LobbySaver,
            lobby_reader: LobbyReader,
            match_saver: MatchSaver,
            id_provider: IdProvider,
    ):
        self.lobby_saver = lobby_saver
        self.lobby_reader = lobby_reader
        self.match_saver = match_saver
        self.id_provider = id_provider

    async def __call__(self, data: PlayerReadyDTO) -> None:
        user = await self.id_provider.get_current_user()

        if not await self.lobby_reader.acceptance_exists(data.acceptance_id):
            raise Exception('acceptance dose not exist')

        await self.lobby_saver.update_acceptance(user.id, data.acceptance_id)

        # lobby_id_1, lobby_id_2 = await self.publish_user_ready(match_id, user_id)

        all_ready: bool = await self.lobby_reader.check_all_ready(data.acceptance_id)
        if all_ready:
            await start_match(
                self.lobby_reader,
                self.match_saver,
                data.acceptance_id,
            )
