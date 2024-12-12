import json
import uuid
from uuid import uuid4

from redis.asyncio import Redis

from backend.repositories.base_redis_repository import BaseRedisRepository
from backend.schemas.lobby_schema import Lobby, AcceptanceMatch, LobbyStatus
from backend.utils.redis_keys import LobbyKeys, UserKeys


class LobbyRepository(BaseRedisRepository):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)

    async def add_to_queue(self, lobby_id: str):
        await self.redis_client.rpush("matchmaking_queue", lobby_id)

    async def lrem(self, name: str, count: int, value: str):
        await self.redis_client.lrem(name, count, value)

    async def remove_from_queue(self, lobby_id: str):
        await self.redis_client.lrem("matchmaking_queue", 0, lobby_id)

    async def get_queue(self) -> list[str]:
        return await self.redis_client.lrange("matchmaking_queue", 0, -1)

    async def create_lobby(self, user_id: int):
        lobby_id = str(uuid4())
        data = Lobby(
            owner_id=user_id,
            players=json.dumps([user_id])
        )
        await self.redis_client.hset(LobbyKeys.lobby(lobby_id), mapping=data.model_dump())
        return lobby_id

    async def get_lobby(self, lobby_id) -> bool:
        exists = await self.redis_client.get(LobbyKeys.lobby(lobby_id))
        return exists > 0

    async def add_player(self, lobby_id: str, user_id: int) -> bool:
        lobby = await self.redis_client.hgetall(LobbyKeys.lobby(lobby_id))
        players = json.loads(lobby.get('players', '[]'))
        if len(players) >= 5 or user_id in players:
            return False

        players.append(user_id)
        updates = {"players": json.dumps(players)}
        if len(players) == 1:
            updates["owner_id"] = user_id

        await self.redis_client.hset(LobbyKeys.lobby(lobby_id), mapping=updates)
        await self.redis_client.set(UserKeys.user_lobby_id(user_id), lobby_id)
        return True

    async def remove_player(self, lobby_id: str, user_id: int):
        lobby = await self.redis_client.hgetall(LobbyKeys.lobby(lobby_id))
        players = json.loads(lobby.get('players', '[]'))
        owner_id = int(lobby.get('owner_id', '0'))

        if user_id not in players:
            return

        players.remove(user_id)
        await self.redis_client.delete(UserKeys.user_lobby_id(user_id))

        if players:
            await self.redis_client.hset(LobbyKeys.lobby(lobby_id), "players", json.dumps(players))

            if owner_id == user_id:
                new_owner_id = players[0]
                await self.redis_client.hset(LobbyKeys.lobby(lobby_id), "owner_id", new_owner_id)
        else:
            await self.redis_client.delete(LobbyKeys.lobby(lobby_id))

    async def all_lobbies(self):
        lobbies = await self.redis_client.keys()
        return lobbies

    async def create_acceptance(self, lobby_id_1: str, lobby_id_2: str) -> tuple[str, list[int]]:
        match_id = str(uuid.uuid4())

        players_1 = await self.redis_client.hget(LobbyKeys.lobby(lobby_id_1), 'players')
        players_2 = await self.redis_client.hget(LobbyKeys.lobby(lobby_id_2), 'players')
        players_1, players_2 = json.loads(players_1), json.loads(players_2)
        all_players = players_1 + players_2
        acceptance: dict[str, bool] = {str(player_id): False for player_id in all_players}
        await self.save_acceptance(match_id, acceptance, lobby_id_1, lobby_id_2)

        await self.redis_client.hset(name=LobbyKeys.lobby(lobby_id_1), key='status', value=LobbyStatus.ACCEPTANCE)
        await self.redis_client.hset(name=LobbyKeys.lobby(lobby_id_2), key='status', value=LobbyStatus.ACCEPTANCE)
        return match_id, all_players

    async def save_acceptance(self, match_id: str, acceptance: dict[str, bool], lobby_id_1: str, lobby_id_2: str):
        # TODO: TTL
        ttl = 10 * 60
        await self.redis_client.hset(LobbyKeys.acceptance(match_id), mapping=acceptance)
        await self.redis_client.expire(LobbyKeys.acceptance(match_id), ttl)
        acceptance_data = AcceptanceMatch(
            match_id=match_id,
            lobby_id_1=lobby_id_1,
            lobby_id_2=lobby_id_2,
        )
        await self.redis_client.hset(LobbyKeys.acceptance_meta(match_id), mapping=acceptance_data.model_dump())
        await self.redis_client.expire(LobbyKeys.acceptance(match_id), ttl)
