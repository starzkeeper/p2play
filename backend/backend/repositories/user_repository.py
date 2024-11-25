from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from backend.db.database import scoped_session
from backend.db.models import User
from backend.schemas.user_schema import FriendshipStatus


class UserRepository:
    model = User

    @classmethod
    async def find_one_or_none(cls, data_id) -> User:
        async with scoped_session() as session:
            query = select(cls.model).filter_by(email=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none_by_id(cls, data_id) -> User:
        async with scoped_session() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **values):
        async with scoped_session() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance

    @classmethod
    async def update(cls, user: User):
        async with scoped_session() as session:
            session.add(user)
            await session.commit()

    @classmethod
    async def insert_steam_id(cls, steam_id: int, user_id: int):
        async with scoped_session() as session:
            user = await session.execute(select(cls.model).filter(User.id == user_id))
            user = user.scalars().first()
            if user and not user.steam_id:
                user.steam_id = steam_id
                await session.commit()
