from abc import abstractmethod
from typing import Protocol

from backend.domain.user.models import UserId, User


class IdProvider(Protocol):
    @abstractmethod
    async def get_current_user_id_access_token(self) -> UserId:
        raise NotImplementedError

    @abstractmethod
    async def get_current_user(self) -> User:
        raise NotImplementedError

    @property
    @abstractmethod
    def refresh_token(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def access_token(self) -> str:
        raise NotImplementedError
