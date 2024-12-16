import json
import logging
from typing import List, Any

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from backend.repositories.base_redis_repository import BaseRedisRepository
from backend.schemas.match_schema import Match
from backend.utils.redis_keys import MatchKeys, LobbyKeys

logger = logging.getLogger('p2play')


class MatchRepository(BaseRedisRepository):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)
        self.pubsub: PubSub = redis_client.pubsub()