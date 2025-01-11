import json
import logging

from redis.asyncio import Redis

from backend.schemas.lobby_schema import LobbyAction, LobbyMessage
from backend.utils.redis_keys import LobbyKeys

logger = logging.getLogger('p2play')


class BaseRedisRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client: Redis = redis_client

    async def set(self, key: str, value: str):
        await self.redis_client.set(key, value)

    async def get(self, key: str):
        return await self.redis_client.get(key)

    async def hgetall(self, key: str):
        return await self.redis_client.hgetall(key)

    async def exists(self, key: str):
        return await self.redis_client.exists(key)

    async def update_lobby_status(self, name: str, status: str):
        await self.redis_client.hset(name, 'lobby_status', status)

    async def publish_lobby_message(self, action: LobbyAction, from_lobby_id: str, message: str,
                                    acceptance_id: str | None = None, user_id: int | str | None = None) -> None:
        logger.debug(f'Lobby message sent: {action}')

        formatted_message = LobbyMessage(
            action=action,
            from_lobby_id=from_lobby_id,
            message=message,
            acceptance_id=acceptance_id,
            user_id=user_id
        )
        await self.redis_client.publish(LobbyKeys.lobby_channel(from_lobby_id),
                                        json.dumps(formatted_message.model_dump(exclude_none=True)))
