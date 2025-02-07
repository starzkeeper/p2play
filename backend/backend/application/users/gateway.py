from abc import abstractmethod
from typing import Protocol

from backend.domain.lobby.models import LobbyId
from backend.domain.user.models import User, UserId


class UserSaver(Protocol):
    @abstractmethod
    async def create_user(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def insert_steam_id(self, steam_id: int, user_id: UserId) -> None:
        raise NotImplementedError


class UserReader(Protocol):
    @abstractmethod
    async def find_one_or_none(self, data_id) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_none_by_id(self, data_id) -> User | None:
        raise NotImplementedError


class UserPubSubInterface(Protocol):
    """
        Sends messages only to user channel
    """

    @abstractmethod
    async def publish_user_joined_message(self, user_id: UserId, lobby_id: LobbyId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_user_left_message(self, user_id: UserId, lobby_id: LobbyId) -> None:
        raise NotImplementedError
