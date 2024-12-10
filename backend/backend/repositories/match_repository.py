from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from backend.repositories.base_redis_repository import BaseRedisRepository


class MatchRepository(BaseRedisRepository):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)
        self.pubsub: PubSub = redis_client.pubsub()
