from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models import Base
from backend.schemas.user_schema import FriendshipStatus

if TYPE_CHECKING:
    from backend.db.models import User
else:
    User = "User"


class Friend(Base):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False, index=True
    )
    friend_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False, index=True
    )
    status: Mapped[FriendshipStatus] = mapped_column(
        Enum(FriendshipStatus), nullable=False, index=True
    )

    # RELATIONSHIPS

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"

    def __repr__(self):
        return str(self)
