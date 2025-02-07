from sqlalchemy import MetaData, Column, DateTime, func
from sqlalchemy.orm import registry

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

meta = MetaData(naming_convention=convention)
mapper_registry = registry(metadata=meta)


def add_timestamps():
    return [
        Column(
            "created_at",
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            server_default=func.now()
        ),
        Column(
            "updated_at",
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            server_default=func.now(),
            onupdate=func.now(),
            server_onupdate=func.now()
        )
    ]
