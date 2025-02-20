import uuid
from dataclasses import dataclass, field
from enum import auto

from backend.domain.common.base_enum import BaseStrEnum
from backend.domain.lobby.models import LobbyId, MatchId
from backend.domain.user.models import UserId


class MatchStatus(BaseStrEnum):
    PREPARATION = auto()
    IN_PROGRESS = auto()


class MatchAction(BaseStrEnum):
    MATCH_PREPARATION_STARTED = auto()
    BAN_MAP = auto()
    BAN_SERVER = auto()
    MATCH_READY = auto()


@dataclass
class Match:
    owner_team_1: UserId
    owner_team_2: UserId
    team_1: list[UserId]
    team_2: list[UserId]
    lobby_id_1: LobbyId
    lobby_id_2: LobbyId
    match_id: MatchId | None = field(default_factory=lambda: str(uuid.uuid4()))
    match_status: MatchStatus = MatchStatus.PREPARATION
