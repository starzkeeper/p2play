import asyncio
import json
import logging
import uuid
from uuid import uuid4

from redis.asyncio import Redis

from backend.exceptions.exceptions import EntityDoesNotExistError
from backend.repositories.base_redis_repository import BaseRedisRepository
from backend.schemas.lobby_schema import Lobby, AcceptanceMatch, LobbyStatus, LobbyMessage, UserAction, UserMessage, \
    LobbyAction, AcceptanceAction, AcceptanceMessage
from backend.schemas.match_schema import Match
from backend.utils.redis_keys import LobbyKeys, UserKeys, MatchKeys

logger = logging.getLogger('p2play')


class LobbyRepository(BaseRedisRepository):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)

    async def add_to_queue(self, lobby_id: str):
        await self.redis_client.rpush("matchmaking_queue", lobby_id)

    async def lrem(self, name: str, count: int, value: str):
        await self.redis_client.lrem(name, count, value)

    async def remove_from_queue(self, lobby_id: str):
        await self.redis_client.lrem("matchmaking_queue", 0, lobby_id)
        await self.update_status(LobbyKeys.lobby(lobby_id), LobbyStatus.WAITING)
        await self.publish_lobby_message(
            action=LobbyAction.STOP_SEARCH,
            message='Lobby stop searching',
            from_lobby_id=lobby_id
        )

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

    async def publish_user_message(self, action: UserAction, user_id: int | str, message: str,
                                   lobby_id: str | None = None) -> None:
        logger.debug(f'User message sent: {action}')

        formatted_message = UserMessage(
            action=action,
            user_id=user_id,
            message=message,
            lobby_id=lobby_id
        )
        await self.redis_client.publish(UserKeys.user_channel(user_id),
                                        json.dumps(formatted_message.model_dump(exclude_none=True)))

    async def publish_lobby_message(self, action: LobbyAction, from_lobby_id: str, message: str,
                                    acceptance_id: str | None = None, user_id: int | str | None = None) -> None:
        logger.debug(f'Lobby message sent: {action}')

        formatted_message = LobbyMessage(
            action=action,
            from_lobby_id=from_lobby_id,
            message=message,
            acceptance_id=acceptance_id,
            user_id=user_id
        )
        await self.redis_client.publish(LobbyKeys.lobby_channel(from_lobby_id),
                                        json.dumps(formatted_message.model_dump(exclude_none=True)))

    async def publish_acceptance_message(self, action: AcceptanceAction, match_id: str, message: str, lobby_id_1: str,
                                         lobby_id_2: str, user_id: int | str | None = None) -> None:
        logger.debug(f'Acceptance message sent: {action}')

        formatted_message = AcceptanceMessage(
            action=action,
            match_id=match_id,
            user_id=user_id,
            message=message
        )
        await self.redis_client.publish(LobbyKeys.lobby_channel(lobby_id_1),
                                        json.dumps(formatted_message.model_dump(exclude_none=True)))
        await self.redis_client.publish(LobbyKeys.lobby_channel(lobby_id_2),
                                        json.dumps(formatted_message.model_dump(exclude_none=True)))

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
        status = lobby.get('status')

        if user_id not in players:
            return

        if status == LobbyStatus.SEARCHING:
            await self.remove_from_queue(lobby_id)

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

        players_1: str = await self.redis_client.hget(LobbyKeys.lobby(lobby_id_1), 'players')
        players_2: str = await self.redis_client.hget(LobbyKeys.lobby(lobby_id_2), 'players')
        players_1: list[int] = json.loads(players_1)
        players_2: list[int] = json.loads(players_2)

        all_players: list[int] = players_1 + players_2
        acceptance: dict[str, bool] = {str(player_id): json.dumps(False) for player_id in all_players}
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
        await self.redis_client.expire(LobbyKeys.acceptance_meta(match_id), ttl)

    async def create_match(self, match_id: str, acceptance_key: str) -> list[str | int]:
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

    async def publish_user_ready(self, match_id: str, user_id: str | int) -> tuple[str, str]:
        acceptance_meta_key: str = LobbyKeys.acceptance_meta(match_id)
        lobby_id_1: str = await self.redis_client.hget(acceptance_meta_key, 'lobby_id_1')
        lobby_id_2: str = await self.redis_client.hget(acceptance_meta_key, 'lobby_id_2')

        await self.publish_acceptance_message(
            action=AcceptanceAction.USER_ACCEPTED,
            user_id=user_id,
            match_id=match_id,
            message=f'User accepted match',
            lobby_id_1=lobby_id_1,
            lobby_id_2=lobby_id_2
        )

        return lobby_id_1, lobby_id_2

    async def start_match(self, match_id: str, acceptance_key: str, lobby_id_1: str, lobby_id_2: str):
        players: list = await self.create_match(match_id, acceptance_key)
        set_tasks = [
            self.set(UserKeys.user_match_id(uid), match_id)
            for uid in players
        ]
        await self.publish_acceptance_message(
            action=AcceptanceAction.JOIN_MATCH,
            match_id=match_id,
            message=f'User accepted match',
            lobby_id_1=lobby_id_1,
            lobby_id_2=lobby_id_2
        )

        await asyncio.gather(*set_tasks)
