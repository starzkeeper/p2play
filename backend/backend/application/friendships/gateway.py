from abc import abstractmethod
from typing import Protocol

from backend.domain.friendship.models import FriendshipId
from backend.domain.user.models import UserId


class FriendshipSaver(Protocol):
    @abstractmethod
    async def create_friend_request(self, friend_id: UserId, user_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def accept_friend_request(self, friend_id: UserId, user_id: UserId) -> None:
        raise NotImplementedError


class FriendshipReader(Protocol):
    @abstractmethod
    async def friend_sent_requests(self, user_id: UserId):
        raise NotImplementedError

    @abstractmethod
    async def friend_received_requests(self, user_id: UserId):
        raise NotImplementedError

    @abstractmethod
    async def all_friends(self, user_id: int):
        raise NotImplementedError
