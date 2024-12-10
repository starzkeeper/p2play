from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from backend.repositories.base_redis_repository import BaseRedisRepository


class WebSocketRepository(BaseRedisRepository):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)
        self.pubsub: PubSub = redis_client.pubsub()

    async def subscribe_to(self, channel_name: str) -> PubSub:
        await self.pubsub.subscribe(channel_name)
        return self.pubsub

    async def unsubscribe_from(self, channel_name: str):
        await self.pubsub.unsubscribe(channel_name)

    async def get_message(self, pubsub: PubSub):
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        return message
