import uuid
from dataclasses import dataclass, field
from typing import NewType

from backend.domain.user.value_objects import EmailField

UserId = NewType("UserId", uuid.UUID)
SteamId = NewType("SteamId", int)


@dataclass
class User:
    email: EmailField
    password: str
    id: UserId = field(default_factory=lambda: uuid.uuid4())
    nickname: str | None = None
    steam_id: SteamId | None = None
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    p2b_balance: float = 0.0
    p2pl_balance: float = 0.0
