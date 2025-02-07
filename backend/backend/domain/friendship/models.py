import uuid
from dataclasses import dataclass, field
from enum import auto
from typing import NewType
from uuid import UUID

from backend.domain.common.base_enum import BaseStrEnum
from backend.domain.user.models import UserId

FriendshipId = NewType('FriendshipId', UUID)


class FriendshipStatus(BaseStrEnum):
    PENDING = auto()
    ACCEPTED = auto()
    DECLINED = auto()


@dataclass
class Friendship:
    user_id: UserId
    friend_id: UserId
    status: FriendshipStatus
    # friendship_id: FriendshipId = field(default_factory=lambda: uuid.uuid4())


