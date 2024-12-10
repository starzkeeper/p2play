from enum import Enum

from pydantic import BaseModel

from backend.repositories.common_schema import MessageAction, ChannelTypes, Message


class MatchStatus(str, Enum):
    WAITING = 'waiting_for_acceptance'
    PREPARATION = 'preparation'
    IN_PROGRESS = "in_progress"


class JoinMatchMessage(Message):
    action: MessageAction = MessageAction.JOIN
    type: ChannelTypes = ChannelTypes.MATCH
    match_id: str


class Match(BaseModel):
    team_1: str
    team_2: str
    acceptance: str
    status: MatchStatus = MatchStatus.WAITING
    lobby_id_1: str
    lobby_id_2: str
