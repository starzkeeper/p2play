import json

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from backend.repositories.base_redis_repository import BaseRedisRepository
from backend.schemas.match_schema import Match
from backend.utils.redis_keys import MatchKeys


class MatchRepository(BaseRedisRepository):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)
        self.pubsub: PubSub = redis_client.pubsub()

    async def create_match(self, match_id: int, acceptance_key: str) -> str:
        lobby_id_1 = await self.hget(acceptance_key, 'lobby_id_1')
        lobby_id_2 = await self.hget(acceptance_key, 'lobby_id_2')
        acceptance = {str(player_id): False for player_id in (players_1 + players_2)}
        match_data = Match(
            team_1=json.dumps(players_1),
            team_2=json.dumps(players_2),
            acceptance=json.dumps(acceptance),
            lobby_id_1=lobby_id_1,
            lobby_id_2=lobby_id_2,
        )
        await self.redis_client.hset(MatchKeys.match(match_id), mapping=match_data.model_dump())
        return match_id
