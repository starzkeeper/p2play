from sqlalchemy import select

from backend.adapters.db.database import scoped_session
from backend.application.errors.exceptions import EntityDoesNotExistError
from backend.application.friendships.gateway import FriendshipReader, FriendshipSaver
from backend.domain.friendship.exceptions import FriendshipAlreadyExists
from backend.domain.friendship.models import FriendshipId, Friendship, FriendshipStatus
from backend.domain.user.models import UserId


class FriendshipGateway(FriendshipSaver, FriendshipReader):
    async def create_friend_request(self, friend_id: UserId, user_id: UserId) -> None:
        async with scoped_session() as session:
            result_existing_friendship = await session.execute(select(Friendship).filter(
                (
                        ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
                        ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id))
                ) &
                (Friendship.status.in_([FriendshipStatus.PENDING, FriendshipStatus.ACCEPTED]))
            ))
            existing_friendship = result_existing_friendship.scalar_one_or_none()
            if existing_friendship:
                raise FriendshipAlreadyExists

            new_friend_request = Friendship(user_id=user_id, friend_id=friend_id, status=FriendshipStatus.PENDING)
            session.add(new_friend_request)
            await session.commit()

    async def accept_friend_request(self, friend_id: UserId, user_id: UserId) -> None:
        async with scoped_session() as session:
            result = await session.execute(select(Friendship).filter(
                ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id) & (
                        Friendship.status == FriendshipStatus.PENDING))
            ))
            friendship = result.scalar_one_or_none()

            if not friendship:
                raise EntityDoesNotExistError

            friendship.status = FriendshipStatus.ACCEPTED
            session.add(friendship)
            await session.commit()

    async def friend_sent_requests(self, user_id: UserId):
        async with scoped_session() as session:
            result_friend_requests = await session.execute(select(Friendship.friend_id).filter(
                (Friendship.user_id == user_id) & (Friendship.status == FriendshipStatus.PENDING)
            ))
            friend_requests = result_friend_requests.scalars().all()
            return friend_requests

    async def friend_received_requests(self, user_id: UserId):
        async with scoped_session() as session:
            result_friend_receives = await session.execute(select(Friendship.user_id).filter(
                (Friendship.friend_id == user_id) & (Friendship.status == FriendshipStatus.PENDING)
            ))
            friend_receives = result_friend_receives.scalars().all()
            return friend_receives

    async def all_friends(self, user_id: int):
        async with scoped_session() as session:
            result = await session.execute(select(Friendship.user_id, Friendship.friend_id).filter(
                ((Friendship.user_id == user_id) | (Friendship.friend_id == user_id)) &
                (Friendship.status == FriendshipStatus.ACCEPTED)
            ))
            friendships = result.all()

            friends = [
                friend if user == user_id else user
                for user, friend in friendships
            ]
            return friends
