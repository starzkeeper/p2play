import logging

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from backend.repositories.base_redis_repository import BaseRedisRepository
from backend.schemas.match_schema import Match
from backend.utils.redis_keys import MatchKeys, LobbyKeys, UserKeys

logger = logging.getLogger('p2play')


class MatchRepository(BaseRedisRepository):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)

    async def get_match(self, user_id: int | str):
        match_id = await self.redis_client.get(UserKeys.user_match_id(user_id))
        if match_id is None:
            return None
        match = self.redis_client.hgetall(MatchKeys.match(match_id))
        return match

