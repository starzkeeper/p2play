import json
import logging
from typing import Optional

from redis.asyncio import Redis

from backend.schemas.common_schema import MessageAction, ChannelTypes, Message
from backend.utils.redis_keys import resolver_channels, UserKeys

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

    async def hget(self, name: str, key: str):
        res = await self.redis_client.hget(name, key)
        return json.loads(res)

    async def hmget(self, name: str, args: list):
        return await self.redis_client.hmget(name, *args)

    async def hset(
            self,
            name: str,
            key: Optional[str] = None,
            value: Optional[str] = None,
            mapping: Optional[dict] = None,
    ):
        if mapping is not None:
            return await self.redis_client.hset(name, mapping=mapping)

        if key is not None and value is not None:
            return await self.redis_client.hset(name, key, value)

        raise ValueError("No valid arguments provided to hset")

    async def update_status(self, name: str, status: str):
        await self.redis_client.hset(name, 'status', status)
