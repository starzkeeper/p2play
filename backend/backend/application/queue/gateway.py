from abc import abstractmethod
from typing import Protocol

from backend.domain.lobby.models import LobbyId


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
