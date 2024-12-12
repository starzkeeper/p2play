from fastapi import HTTPException
from sqlalchemy import select

from backend.db.database import scoped_session
from backend.db.models import Friend
from backend.exceptions.exceptions import InvalidOperationError, EntityDoesNotExistError
from backend.schemas.user_schema import FriendshipStatus


class FriendRepository:
    model = Friend

    @classmethod
    async def create_friend_request(cls, friend_id: int, user_id: int):
        async with scoped_session() as session:
            result_existing_friendship = await session.execute(select(cls.model).filter(
                (
                        ((cls.model.user_id == user_id) & (cls.model.friend_id == friend_id)) |
                        ((cls.model.user_id == friend_id) & (cls.model.friend_id == user_id))
                ) &
                (cls.model.status.in_([FriendshipStatus.PENDING, FriendshipStatus.ACCEPTED]))
            ))
            existing_friendship = result_existing_friendship.scalar_one_or_none()
            if existing_friendship:
                raise InvalidOperationError

            new_friend_request = cls.model(user_id=user_id, friend_id=friend_id, status=FriendshipStatus.PENDING)
            session.add(new_friend_request)
            await session.commit()

    @classmethod
    async def friend_sent_requests(cls, user_id: int):
        async with scoped_session() as session:
            result_friend_requests = await session.execute(select(cls.model.friend_id).filter(
                (cls.model.user_id == user_id) & (cls.model.status == FriendshipStatus.PENDING)
            ))
            friend_requests = result_friend_requests.scalars().all()
            return friend_requests

    @classmethod
    async def friend_received_requests(cls, user_id: int):
        async with scoped_session() as session:
            result_friend_receives = await session.execute(select(cls.model.user_id).filter(
                (cls.model.friend_id == user_id) & (cls.model.status == FriendshipStatus.PENDING)
            ))
            friend_receives = result_friend_receives.scalars().all()
            return friend_receives

    @classmethod
    async def accept_friend_request(cls, friend_id: int, user_id: int):
        async with scoped_session() as session:
            result = await session.execute(select(cls.model).filter(
                ((cls.model.user_id == friend_id) & (cls.model.friend_id == user_id) & (
                        cls.model.status == FriendshipStatus.PENDING))
            ))
            friendship = result.scalar_one_or_none()

            if not friendship:
                raise EntityDoesNotExistError

            friendship.status = FriendshipStatus.ACCEPTED
            session.add(friendship)
            await session.commit()

    @classmethod
    async def all_friends(cls, user_id: int):
        async with scoped_session() as session:
            result = await session.execute(select(cls.model.user_id, cls.model.friend_id).filter(
                ((cls.model.user_id == user_id) | (cls.model.friend_id == user_id)) &
                (cls.model.status == FriendshipStatus.ACCEPTED)
            ))
            friendships = result.all()

            friends = [
                friend if user == user_id else user
                for user, friend in friendships
            ]
            return friends
