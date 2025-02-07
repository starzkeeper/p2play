from abc import abstractmethod
from typing import Protocol


class SteamInterface(Protocol):
    @abstractmethod
    def create_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate_response(self, callback_data: dict) -> str:
        raise NotImplementedError
