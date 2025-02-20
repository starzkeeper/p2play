from dataclasses import dataclass

from backend.application.common.interactor import Interactor
from backend.application.match.gateway import MatchReader, MatchPubSubInterface
from backend.domain.lobby.models import MatchId
from backend.domain.match.exceptions import ActionIsNotAllowed
from backend.domain.match.models import MatchAction, Match
from backend.domain.user.models import UserId


@dataclass
class BroadcastBanMapMessageInputDTO:
    user_id: UserId
    match_id: MatchId


class BroadcastBanMapMessage(Interactor[BroadcastBanMapMessageInputDTO, None]):
    def __init__(
            self,
            match_reader: MatchReader,
            match_pubsub: MatchPubSubInterface
    ):
        self.match_reader = match_reader
        self.match_pubsub = match_pubsub

    async def __call__(self, data: BroadcastBanMapMessageInputDTO) -> None:
        match: Match = await self.match_reader.get_match(data.match_id)
        if data.user_id in (match.owner_team_1, match.owner_team_2):
            await self.match_pubsub.publish_match_user_ban_map(match.match_id)
