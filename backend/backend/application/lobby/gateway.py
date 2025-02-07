from abc import abstractmethod
from typing import Protocol

from backend.domain.lobby.models import Lobby, LobbyId
from backend.domain.match.models import MatchId
from backend.domain.user.models import UserId


class LobbySaver(Protocol):

    @abstractmethod
    async def set_player_lobby(self, lobby_id: LobbyId, user_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def clear_user_lobby(self, user_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_lobby(self, lobby_id: LobbyId, version: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_lobby(self, lobby: Lobby, version: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_lobby(self, lobby: Lobby) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_player_to_lobby(self, lobby_id: LobbyId, user_id: UserId, version: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_acceptance(self, match_id: MatchId, acceptance: dict) -> None:  # Временное решение
        raise NotImplementedError

    @abstractmethod
    async def update_acceptance(self, user_id: UserId, match_id: MatchId) -> None:  # Временное решение
        raise NotImplementedError

    @abstractmethod
    async def create_acceptance_meta(self, match_id: MatchId, lobby_id_1: LobbyId,
                                     lobby_id_2: LobbyId) -> None:  # Временное решение
        raise NotImplementedError


class LobbyReader(Protocol):

    @abstractmethod
    async def get_players(self, lobby_id: LobbyId) -> list[UserId]:
        raise NotImplementedError

    @abstractmethod
    async def lobby_exists(self, lobby_id: LobbyId) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_lobby(self, lobby_id: LobbyId) -> (Lobby, int):
        raise NotImplementedError

    @abstractmethod
    async def get_user_lobby_id(self, user_id: UserId) -> LobbyId | None:
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


class LobbyPubSubInterface(Protocol):
    """
        Sends messages only to lobby channel
    """
    @abstractmethod
    async def publish_user_joined_message(self, user_id: UserId, lobby_id: LobbyId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_user_left_message(self, user_id: UserId, lobby_id: LobbyId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_lobby_start_searching(self, lobby_id: LobbyId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_lobby_stop_searching(self, lobby_id: LobbyId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_lobby_match_found(self, lobby_id: LobbyId, match_id: MatchId) -> None:
        raise NotImplementedError


class QueueSaver(Protocol):

    @abstractmethod
    async def take_id_from_queue(self) -> LobbyId:  # Временное решение
        raise NotImplementedError

    @abstractmethod
    async def add_to_queue(self, lobby_id: LobbyId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_from_queue(self, lobby_id: LobbyId) -> None:
        raise NotImplementedError


class QueueReader(Protocol):
    @abstractmethod
    async def get_queue_len(self) -> int:  # Временное решение
        raise NotImplementedError
