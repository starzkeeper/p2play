import json
from typing import Optional

from pydantic import BaseModel
from redis.asyncio import Redis

from backend.schemas.lobby_schema import Recipient


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

    async def publish_message(self, channel_name: str, message: BaseModel, recipient: Recipient):
        message_dict = message.model_dump()
        message_dict['recipient'] = recipient
        await self.redis_client.publish(channel_name, json.dumps(message_dict))
