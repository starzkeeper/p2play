from abc import abstractmethod
from typing import Protocol

from backend.domain.match.models import Match, MatchId


class MatchSaver(Protocol):
    @abstractmethod
    async def create_match(self, match: Match) -> None:
        raise NotImplementedError


class MatchReader(Protocol):
    @abstractmethod
    async def get_match(self, match_id: MatchId) -> Match:
        raise NotImplementedError
