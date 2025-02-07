import logging

from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from backend.adapters.db.database import scoped_session
from backend.adapters.messages.user import UserMessage
from backend.adapters.persistence.redis_keys import UserKeys, RefreshKeys
from backend.application.errors.user import UserNotFound
from backend.application.users.gateway import UserSaver, UserReader, UserPubSubInterface
from backend.domain.lobby.models import UserAction, LobbyId
from backend.domain.user.models import User, UserId

logger = logging.getLogger('p2play')


class UserGateway(UserReader, UserSaver):
    async def create_user(self, user: User) -> None:
        async with scoped_session() as session:
            try:
                session.add(user)
                await session.commit()
            except IntegrityError as e:
                logger.debug(f"Integrity error: {e}")
                raise
            except SQLAlchemyError as e:
                logger.debug(f"Database error: {e}")
                raise

    async def update(self, user: User) -> None:
        async with scoped_session() as session:
            try:
                await session.merge(user)
                await session.commit()
            except IntegrityError as e:
                logger.debug(f"Integrity error: {e}")
                raise
            except SQLAlchemyError as e:
                logger.debug(f"Database error: {e}")
                raise

    async def insert_steam_id(self, steam_id: int, user_id: UserId) -> None:
        async with scoped_session() as session:
            try:
                result = await session.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(steam_id=steam_id)
                    .execution_options(synchronize_session=False)
                )
                if result.rowcount == 0:
                    raise UserNotFound
                await session.commit()
            except SQLAlchemyError as e:
                print(f"Ошибка базы данных: {e}")
                raise

    async def find_one_or_none(self, data_id) -> User | None:
        async with scoped_session() as session:
            query = select(User).filter_by(email=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def find_one_or_none_by_id(self, data_id) -> User | None:
        async with scoped_session() as session:
            query = select(User).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()


class UserPubSubGateway(UserPubSubInterface):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def publish_user_joined_message(self, user_id: UserId, lobby_id: LobbyId) -> None:
        message = UserMessage(
            user_id=user_id,
            action=UserAction.JOIN_LOBBY,
            message='User joined lobby',
            lobby_id=lobby_id

        )
        await self.redis_client.publish(UserKeys.user_channel(user_id), message.model_dump_json(exclude_none=True))

    async def publish_user_left_message(self, user_id: UserId, lobby_id: LobbyId) -> None:
        message = UserMessage(
            user_id=user_id,
            action=UserAction.LEAVE_LOBBY,
            message='User left lobby',
            lobby_id=lobby_id

        )
        await self.redis_client.publish(UserKeys.user_channel(user_id), message.model_dump_json(exclude_none=True))
