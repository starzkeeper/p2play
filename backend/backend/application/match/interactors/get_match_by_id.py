from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.match.gateway import MatchReader
from backend.domain.lobby.models import MatchId
from backend.domain.match.models import Match
from backend.domain.match.service import check_user_in_match


class GetMatchById(Interactor[MatchId, Match]):
    def __init__(
            self,
            id_provider: IdProvider,
            match_reader: MatchReader
    ):
        self.id_provider = id_provider
        self.match_reader = match_reader

    async def __call__(self, data: MatchId) -> Match:
        user = await self.id_provider.get_current_user()
        match: Match = await self.match_reader.get_match(data)
        check_user_in_match(match, user.id)
        return match
