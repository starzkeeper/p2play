import asyncio
import json
import logging
import uuid
from uuid import uuid4

from redis.asyncio import Redis

from backend.exceptions.exceptions import EntityDoesNotExistError, EntityAlreadyExistsError, InvalidOperationError
from backend.repositories.base_redis_repository import BaseRedisRepository
from backend.schemas.lobby_schema import Lobby, AcceptanceMatch, LobbyStatus, UserAction, UserMessage, \
    LobbyAction, AcceptanceAction, AcceptanceMessage, UserLobbyAction
from backend.schemas.match_schema import Match
from backend.utils.redis_keys import LobbyKeys, UserKeys, MatchKeys

logger = logging.getLogger('p2play')


class LobbyRepository(BaseRedisRepository):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)

    async def add_to_queue(self, user_id: int | str):
        # TODO: Sorted list
        lobby_id = await self.redis_client.get(UserKeys.user_lobby_id(user_id))
        await self.check_user_is_owner(lobby_id, user_id)

        add_queue = await self.redis_client.sadd("matchmaking_queue", lobby_id)
        if add_queue == 1:
            await self.update_lobby_status(LobbyKeys.lobby(lobby_id), LobbyStatus.SEARCHING)
            await self.publish_lobby_message(
                action=LobbyAction.START_SEARCH,
                message='Start searching match',
                from_lobby_id=lobby_id,
            )
        else:
            pass

    async def check_user_is_owner(self, lobby_id: str, user_id: int | str):
        if not lobby_id:
            raise InvalidOperationError
        owner_id = await self.redis_client.hget(LobbyKeys.lobby(lobby_id), 'owner_id')

        if int(owner_id) != int(user_id):
            raise InvalidOperationError

    async def remove_from_queue(self, lobby_id: str):
        await self.redis_client.srem("matchmaking_queue", lobby_id)
        await self.update_lobby_status(LobbyKeys.lobby(lobby_id), LobbyStatus.WAITING)
        await self.publish_lobby_message(
            action=LobbyAction.STOP_SEARCH,
            message='Lobby stop searching',
            from_lobby_id=lobby_id
        )

    async def get_queue(self) -> list[str]:
        return await self.redis_client.smembers("matchmaking_queue")

    async def get_len_queue(self) -> int:
        return await self.redis_client.scard("matchmaking_queue")

    async def create_lobby(self, user_id: int):
        lobby_id = str(uuid4())
        data = Lobby(
            owner_id=user_id,
            players=json.dumps([user_id])
        )
        await self.redis_client.hset(LobbyKeys.lobby(lobby_id), mapping=data.model_dump())
        await self.redis_client.set(UserKeys.user_lobby_id(user_id), lobby_id)
        await self.publish_user_joined_event(user_id=user_id, lobby_id=lobby_id)
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

    async def publish_user_joined_event(self, user_id: int | str, lobby_id: str) -> None:
        await self.publish_user_message(
            action=UserAction.JOIN_LOBBY,
            user_id=user_id,
            message=f'{user_id} joined lobby',
            lobby_id=lobby_id
        )
        await self.publish_lobby_message(
            action=UserLobbyAction.USER_JOINED_MESSAGE,
            user_id=user_id,
            message=f'{user_id} joined lobby',
            from_lobby_id=lobby_id
        )

    async def publish_user_left_event(self, user_id: int | str, lobby_id: str) -> None:
        await self.publish_user_message(
            action=UserAction.LEAVE_LOBBY,
            user_id=user_id,
            message=f'{user_id} left the lobby',
            lobby_id=lobby_id
        )
        await self.publish_lobby_message(
            action=UserLobbyAction.USER_LEFT_MESSAGE,
            user_id=user_id,
            message=f'{user_id} left the lobby',
            from_lobby_id=lobby_id
        )

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

    async def publish_lobby_match_ready(self, match_id: str, lobby_id_1: str, lobby_id_2: str) -> None:
        await self.publish_lobby_message(
            action=LobbyAction.ACCEPT_MATCH,
            message=f"Match waiting for acceptance",
            from_lobby_id=lobby_id_1,
            acceptance_id=match_id
        ),
        await self.publish_lobby_message(
            action=LobbyAction.ACCEPT_MATCH,
            message=f"Match waiting for acceptance",
            from_lobby_id=lobby_id_2,
            acceptance_id=match_id
        )

    async def check_existed_lobby(self, user_id: int | str, lobby_id: str):
        if not await self.redis_client.exists(LobbyKeys.lobby(lobby_id)):
            raise EntityDoesNotExistError('Lobby')

        existed_lobby: str = await self.redis_client.get(UserKeys.user_lobby_id(user_id))

        if existed_lobby == lobby_id:
            raise EntityAlreadyExistsError

        elif existed_lobby:
            await self.remove_player(existed_lobby, user_id)

    async def add_player(self, lobby_id: str, user_id: int) -> bool:
        await self.check_existed_lobby(user_id, lobby_id)

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

        await self.publish_user_joined_event(user_id, lobby_id)

    async def remove_player(self, lobby_id: str, user_id: int):
        lobby = await self.redis_client.hgetall(LobbyKeys.lobby(lobby_id))
        players = json.loads(lobby.get('players', '[]'))
        owner_id = int(lobby.get('owner_id', '0'))
        status = lobby.get('lobby_status')

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

        await self.publish_user_left_event(user_id, lobby_id)

    async def all_lobbies(self):
        lobbies = await self.redis_client.keys()
        return lobbies

    async def lobby_selection(self) -> tuple[str, str]:
        # TODO: algorithm, condition race fix, search missing players
        lobby_id_1 = await self.redis_client.spop("matchmaking_queue")
        lobby_id_2 = await self.redis_client.spop("matchmaking_queue")
        return lobby_id_1, lobby_id_2

    async def create_acceptance(self) -> tuple[str, list[int]]:
        queue = await self.get_len_queue()
        if queue < 2:
            return
        lobby_id_1, lobby_id_2 = await self.lobby_selection()

        match_id = str(uuid.uuid4())

        players_1: str = await self.redis_client.hget(LobbyKeys.lobby(lobby_id_1), 'players')
        players_2: str = await self.redis_client.hget(LobbyKeys.lobby(lobby_id_2), 'players')
        players_1: list[int] = json.loads(players_1)
        players_2: list[int] = json.loads(players_2)

        all_players: list[int] = players_1 + players_2
        acceptance: dict[str, bool] = {str(player_id): json.dumps(False) for player_id in all_players}
        await self.save_acceptance(match_id, acceptance, lobby_id_1, lobby_id_2)

        await self.redis_client.hset(name=LobbyKeys.lobby(lobby_id_1), key='lobby_status', value=LobbyStatus.ACCEPTANCE)
        await self.redis_client.hset(name=LobbyKeys.lobby(lobby_id_2), key='lobby_status', value=LobbyStatus.ACCEPTANCE)

        await self.publish_lobby_match_ready(match_id, lobby_id_1, lobby_id_2)

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

    async def player_ready(self, match_id: str, user_id: str | int):
        acceptance_key: str = LobbyKeys.acceptance(match_id)
        if not await self.exists(acceptance_key):
            raise EntityDoesNotExistError('Match')

        await self.redis_client.hset(acceptance_key, str(user_id), json.dumps(True))

        lobby_id_1, lobby_id_2 = await self.publish_user_ready(match_id, user_id)

        all_ready: bool = await self.check_all_ready(acceptance_key)
        if all_ready:
            asyncio.create_task(
                self.start_match(match_id, lobby_id_1, lobby_id_2)
            )

    async def start_match(self, match_id: str, lobby_id_1: str, lobby_id_2: str):
        await self.create_match(match_id, lobby_id_1, lobby_id_2)
        await self.publish_acceptance_message(
            action=AcceptanceAction.JOIN_MATCH,
            match_id=match_id,
            message=f'Match started',
            lobby_id_1=lobby_id_1,
            lobby_id_2=lobby_id_2
        )

    async def create_match(self, match_id: str, lobby_id_1: str, lobby_id_2: str) -> list[str | int]:
        match_info_1, match_info_2 = await asyncio.gather(
            self.redis_client.hmget(LobbyKeys.lobby(lobby_id_1), ["players", "owner_id"]),
            self.redis_client.hmget(LobbyKeys.lobby(lobby_id_2), ["players", "owner_id"]),
        )
        players_json_1, owner_id_1 = match_info_1
        players_json_2, owner_id_2 = match_info_2

        match_data = Match(
            owner_team_1=owner_id_1,
            owner_team_2=owner_id_2,
            team_1=players_json_1,
            team_2=players_json_2,
            lobby_id_1=lobby_id_1,
            lobby_id_2=lobby_id_2,
        )
        await self.redis_client.hset(MatchKeys.match(match_id), mapping=match_data.model_dump())
        logger.debug(f'Create Match: {self.__class__}')

        players_1: list = json.loads(players_json_1)
        players_2: list = json.loads(players_json_2)
        set_tasks = [
            self.set(UserKeys.user_match_id(uid), match_id)
            for uid in players_1 + players_2
        ]
        await asyncio.gather(*set_tasks)

