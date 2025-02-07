from abc import abstractmethod
from typing import Protocol

from backend.domain.lobby.models import LobbyId, MatchId
from backend.domain.user.models import UserId


class PubSubInterface(Protocol):
    @abstractmethod
    async def subscribe_user_channel(self, user_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def unsubscribe_user_channel(self, user_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def subscribe_lobby_channel(self, lobby_id: LobbyId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def unsubscribe_lobby_channel(self, lobby_id: LobbyId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def subscribe_match_channel(self, match_id: MatchId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def unsubscribe_match_channel(self, match_id: MatchId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def listen_channel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def start_listening(self) -> None:
        raise NotImplementedError

    async def stop_listening(self) -> None:
        raise NotImplementedError
