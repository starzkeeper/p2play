from abc import abstractmethod
from typing import Protocol

from backend.domain.user.models import UserId


class RefreshSaver(Protocol):
    @abstractmethod
    async def save_refresh_token(self, user_id: UserId, refresh_token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_refresh_token(self, refresh_token: str) -> None:
        raise NotImplementedError


class RefreshReader(Protocol):
    @abstractmethod
    async def read_refresh_token(self, refresh_token: str) -> UserId:
        raise NotImplementedError
