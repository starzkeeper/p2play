import logging
from dataclasses import dataclass

from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.lobby.services_interface import MatchServiceInterface
from backend.application.match.gateway import MatchSaver, MatchReader
from backend.application.match.interactors.create_match import CreateMatchInputDTO
from backend.domain.match.models import MatchId

logger = logging.getLogger('p2play')


@dataclass
class PlayerReadyDTO:
    acceptance_id: MatchId


class PlayerReady(Interactor[PlayerReadyDTO, None]):
    def __init__(
            self,
            match_reader: MatchReader,
            match_saver: MatchSaver,
            id_provider: IdProvider,
            match_service: MatchServiceInterface,
    ):
        self.match_reader = match_reader
        self.match_saver = match_saver
        self.id_provider = id_provider
        self.match_service = match_service

    async def __call__(self, data: PlayerReadyDTO) -> None:
        user = await self.id_provider.get_current_user()

        if not await self.match_reader.acceptance_exists(data.acceptance_id):
            raise Exception('acceptance dose not exist')

        await self.match_saver.update_acceptance(user.id, data.acceptance_id)

        # lobby_id_1, lobby_id_2 = await self.publish_user_ready(match_id, user_id)

        await self.match_service.create_match(CreateMatchInputDTO(
            acceptance_id=data.acceptance_id,
        ))
