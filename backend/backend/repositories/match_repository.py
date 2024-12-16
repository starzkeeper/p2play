import json
import logging

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

    async def create_match(self, match_id: int, acceptance_key: str) -> str:
        acceptance_meta_key = LobbyKeys.acceptance_meta(match_id)
        lobby_id_1: str = await self.redis_client.hget(acceptance_meta_key, 'lobby_id_1')
        lobby_id_2: str = await self.redis_client.hget(acceptance_meta_key, 'lobby_id_2')
        logger.debug([lobby_id_1, lobby_id_2])

        players_json_1: str = await self.redis_client.hget(LobbyKeys.lobby(lobby_id_1), 'players')
        players_json_2: str = await self.redis_client.hget(LobbyKeys.lobby(lobby_id_2), 'players')
        players_1: list = json.loads(players_json_1)
        players_2: list = json.loads(players_json_2)

        match_data = Match(
            team_1=players_json_1,
            team_2=players_json_2,
            lobby_id_1=lobby_id_1,
            lobby_id_2=lobby_id_2,
        )
        await self.redis_client.hset(MatchKeys.match(match_id), mapping=match_data.model_dump())
        logger.debug(f'Create Match: {self.__class__}')
        return players_1 + players_2

    async def check_all_ready(self, acceptance_key: str) -> bool:
        acceptance = await self.redis_client.hvals(acceptance_key)
        return all(json.loads(value) for value in acceptance)