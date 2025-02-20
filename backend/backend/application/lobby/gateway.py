from abc import abstractmethod
from typing import Protocol

from backend.adapters.messages.lobby import LobbyMessage
from backend.domain.lobby.models import Lobby, LobbyId, UserLobbyAction
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


class LobbyReader(Protocol):

    @abstractmethod
    async def lobby_exists(self, lobby_id: LobbyId) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_lobby(self, lobby_id: LobbyId) -> (Lobby, int):
        raise NotImplementedError

    @abstractmethod
    async def get_user_lobby_id(self, user_id: UserId) -> LobbyId | None:
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
    async def publish_lobby_user_message(self, user_id: UserId, lobby_id: LobbyId, message: str) -> None:
        raise NotImplementedError
