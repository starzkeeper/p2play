from redis.asyncio import Redis

from backend.domain.lobby.models import MatchId


class BanSelectionAdapter:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def start_selection(self, match_id: MatchId, available_options: list):
        key_options = f'match:{match_id}:available_options'
        key_submission = f'match:{match_id}:submission'

        await self.redis_client.delete(key_options)
        for option in available_options:
            await self.redis_client.rpush(key_options, option)