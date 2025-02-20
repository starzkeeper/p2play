from abc import abstractmethod
from typing import Protocol

from backend.application.match.interactors.create_match import CreateMatchInputDTO
from backend.application.queue.interactors.add_lobby_to_queue import QueueInputDTO
from backend.application.queue.interactors.remove_lobby_from_queue import RemoveFromQueueInputDTO


class QueueServiceInterface(Protocol):
    @abstractmethod
    async def add_to_queue(self, data: QueueInputDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_from_queue(self, data: RemoveFromQueueInputDTO) -> None:
        raise NotImplementedError


class MatchServiceInterface(Protocol):
    @abstractmethod
    async def create_acceptance(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_match(self, data: CreateMatchInputDTO) -> None:
        raise NotImplementedError
