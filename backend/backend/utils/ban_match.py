from redis.asyncio import Redis


class MatchBanController:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client