import sqlalchemy as sa
from sqlalchemy import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, composite

from backend.adapters.db.models import mapper_registry
from backend.adapters.db.models.base import add_timestamps
from backend.domain.user.models import User
from backend.domain.user.value_objects import EmailField

users_table = sa.Table(
    "users",
    mapper_registry.metadata,
    sa.Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False
    ),
    sa.Column("user_email", sa.String, unique=True, nullable=False, index=True),
    sa.Column("password", sa.String, nullable=False, index=True),
    sa.Column("nickname", sa.String(255), unique=True, nullable=False, index=True),
    sa.Column("p2b_balance", sa.Float, nullable=False, server_default="0"),
    sa.Column("p2pl_balance", sa.Float, nullable=False, server_default="0"),
    sa.Column("steam_id", sa.BigInteger, unique=True, nullable=True),
    sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
    sa.Column("is_verified", sa.Boolean, nullable=False, server_default=sa.text("false")),
    sa.Column("is_superuser", sa.Boolean, nullable=False, server_default=sa.text("false")),
    *add_timestamps()
)


def map_users_table() -> None:
    mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            "requested_rels": relationship(
                'Friendship',
                foreign_keys='Friendship.user_id',
                backref='requesting_user'
            ),
            "received_rels": relationship(
                'Friendship',
                foreign_keys='Friendship.friend_id',
                backref='receiving_user'
            ),
            "email": composite(EmailField, users_table.c.user_email)
        },
    )


User.aspiring_friends = association_proxy("received_rels", "requesting_user")
User.desired_friends = association_proxy("requested_rels", "receiving_user")
