import sqlalchemy as sa

from backend.adapters.db.models import mapper_registry
from backend.adapters.db.models.base import add_timestamps
from backend.domain.friendship.models import FriendshipStatus, Friendship

friendships_table = sa.Table(
    "friendships",
    mapper_registry.metadata,
    sa.Column("friendship_id", sa.Integer, primary_key=True, nullable=False, autoincrement=True),
    sa.Column(
        "user_id", sa.UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    ),
    sa.Column(
        "friend_id", sa.UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    ),
    sa.Column(
        "status", sa.Enum(FriendshipStatus), nullable=False, index=True
    ),
    *add_timestamps()
)


def map_friendships_table():
    mapper_registry.map_imperatively(Friendship, friendships_table)
