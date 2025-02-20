from abc import abstractmethod
from typing import Protocol

from backend.domain.lobby.models import LobbyId
from backend.domain.match.models import Match, MatchId, MatchAction
from backend.domain.user.models import UserId


class MatchSaver(Protocol):
    @abstractmethod
    async def create_match(self, match: Match) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_acceptance(self, user_id: UserId, match_id: MatchId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_acceptance_meta(self, match_id: MatchId, lobby_id_1: LobbyId,
                                     lobby_id_2: LobbyId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_acceptance(self, match_id: MatchId, acceptance: dict) -> None:
        raise NotImplementedError


class MatchReader(Protocol):
    @abstractmethod
    async def get_match(self, match_id: MatchId) -> Match:
        raise NotImplementedError

    @abstractmethod
    async def acceptance_exists(self, acceptance_id: LobbyId) -> bool:  # Временное решение
        raise NotImplementedError

    @abstractmethod
    async def check_all_ready(self, acceptance_id: str) -> bool:  # Временное решение
        raise NotImplementedError

    @abstractmethod
    async def get_acceptance_meta(self, acceptance_id: str) -> tuple[LobbyId, LobbyId]:  # Временное решение
        raise NotImplementedError


class MatchPubSubInterface(Protocol):
    @abstractmethod
    async def publish_lobby_match_found(self, lobby_id: LobbyId, match_id: MatchId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_match_preparation_started(self, match_id: MatchId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_match_user_ban_map(self, match_id: MatchId) -> None:
        raise NotImplementedError
