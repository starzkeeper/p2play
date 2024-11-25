from typing import TYPE_CHECKING

from sqlalchemy import String, Float, Integer, Boolean, text, BigInteger
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base

if TYPE_CHECKING:
    from backend.db.models import Friend
else:
    Friend = 'Friend'


class User(Base):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(
        String, index=True, unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(
        String, index=True, nullable=False
    )
    nickname: Mapped[str] = mapped_column(
        String(255), index=True, unique=True, nullable=True
    )
    p2b_balance: Mapped[float] = mapped_column(
        Float, index=False, nullable=False, server_default='0'
    )
    p2pl_balance: Mapped[float] = mapped_column(
        Float, index=False, nullable=False, server_default='0'
    )
    steam_id: Mapped[int] = mapped_column(
        BigInteger, index=False, nullable=True, unique=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, index=False, nullable=False, server_default=text('true')
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, index=False, nullable=False, server_default=text('false')
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, index=False, nullable=False, server_default=text('false')
    )

    # RELATIONSHIPS
    requested_rels = relationship(
        'Friend',
        foreign_keys='Friend.user_id',
        backref='requesting_user'
    )
    received_rels = relationship(
        'Friend',
        foreign_keys='Friend.friend_id',
        backref='receiving_user'
    )
    aspiring_friends = association_proxy('received_rels', 'requesting_user')
    desired_friends = association_proxy('requested_rels', 'receiving_user')

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"

    def __repr__(self):
        return str(self)
