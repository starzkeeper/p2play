import uuid

from redis.asyncio import Redis

from backend.application.queue.gateway import QueueReader, QueueSaver
from backend.domain.lobby.models import LobbyId


class QueueGateway(QueueReader, QueueSaver):
    def __init__(
            self,
            redis_client: Redis
    ):
        self.redis_client: Redis = redis_client

    async def get_queue_len(self) -> int:
        return await self.redis_client.scard('matchmaking_queue')

    async def take_id_from_queue(self) -> LobbyId:
        lobby_id = await self.redis_client.spop('matchmaking_queue')
        return LobbyId(uuid.UUID(lobby_id))

    async def add_to_queue(self, lobby_id: LobbyId) -> None:
        await self.redis_client.sadd('matchmaking_queue', str(lobby_id))

    async def remove_from_queue(self, lobby_id: LobbyId) -> None:
        await self.redis_client.srem('matchmaking_queue', str(lobby_id))
