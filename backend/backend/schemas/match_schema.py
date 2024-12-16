from enum import Enum

from pydantic import BaseModel

from backend.schemas.common_schema import Message


class MatchStatus(str, Enum):
    PREPARATION = 'preparation'
    IN_PROGRESS = "in_progress"


class MatchMessage(Message):
    from_match_id: str


class Match(BaseModel):
    team_1: str
    team_2: str
    status: MatchStatus = MatchStatus.PREPARATION
    lobby_id_1: str
    lobby_id_2: str
