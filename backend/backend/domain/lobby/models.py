import uuid
from dataclasses import dataclass, field
from enum import auto
from typing import NewType

from backend.domain.common.base_enum import BaseStrEnum
from backend.domain.user.models import UserId

LobbyId = NewType('LobbyId', uuid.UUID)
MatchId = NewType('MatchId', uuid.UUID)


class LobbyStatus(BaseStrEnum):
    WAITING = auto()
    SEARCHING = auto()
    ACCEPTANCE = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()


class UserAction(BaseStrEnum):
    # Redis
    JOIN_LOBBY = auto()
    LEAVE_LOBBY = auto()


class LobbyAction(BaseStrEnum):
    START_SEARCH = auto()
    STOP_SEARCH = auto()

    # Redis
    ACCEPT_MATCH = auto()


class UserLobbyAction(BaseStrEnum):
    USER_JOINED_MESSAGE = auto()
    USER_LEFT_MESSAGE = auto()
    MESSAGE_LOBBY = auto()


class AcceptanceAction(BaseStrEnum):
    USER_ACCEPTED = auto()

    # REDIS
    JOIN_MATCH = auto()
    CANCEL_MATCH = auto()


@dataclass
class Lobby:
    players: list[UserId]
    owner_id: UserId
    lobby_id: LobbyId = field(default_factory=lambda: uuid.uuid4())
    lobby_status: LobbyStatus = LobbyStatus.WAITING
    match_id: MatchId | None = None


@dataclass
class AcceptanceMatch:
    match_id: str
    lobby_id_1: str
    lobby_id_2: str
