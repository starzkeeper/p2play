from backend.application.lobby.services_interface import MatchServiceInterface
from backend.application.match.interactors.create_acceptance import CreateAcceptance
from backend.application.match.interactors.create_match import CreateMatchInputDTO, CreateMatch


class MatchServiceGateway(MatchServiceInterface):
    def __init__(
            self,
            create_acceptance: CreateAcceptance,
            create_match: CreateMatch,
    ):
        self.create_acceptance = create_acceptance
        self.create_match = create_match

    async def create_acceptance(self) -> None:
        await self.create_acceptance()

    async def create_match(self, data: CreateMatchInputDTO) -> None:
        await self.create_match(data)
