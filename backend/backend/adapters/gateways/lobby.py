import json
import logging
import uuid
from dataclasses import asdict

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from redis.asyncio import Redis

from backend.adapters.messages.lobby import LobbyMessage
from backend.adapters.persistence.redis_keys import UserKeys, LobbyKeys
from backend.application.errors.exceptions import OptimisticLockException
from backend.application.errors.lobby import LobbyDoesNotExist
from backend.application.lobby.gateway import LobbySaver, LobbyReader, LobbyPubSubInterface
from backend.domain.lobby.models import LobbyId, Lobby, UserLobbyAction, LobbyAction
from backend.domain.match.models import MatchId
from backend.domain.user.models import UserId

logger = logging.getLogger('p2play')


class LobbyGateway(LobbySaver, LobbyReader):

    def __init__(
            self,
            mongo_db: AsyncDatabase,
            redis_client: Redis
    ):
        self.redis_client: Redis = redis_client
        self.collection: AsyncCollection = mongo_db['lobby']

    async def set_player_lobby(self, lobby_id: LobbyId, user_id: UserId) -> None:
        await self.redis_client.set(UserKeys.user_lobby_id(str(user_id)), str(lobby_id))

    async def clear_user_lobby(self, user_id: UserId) -> None:
        print('cleared')
        await self.redis_client.delete(UserKeys.user_lobby_id(str(user_id)))

    async def delete_lobby(self, lobby_id: LobbyId, version: int) -> None:
        result = await self.collection.delete_one(
            {"lobby_id": lobby_id, "version": version}
        )

        if result.deleted_count == 0:
            raise OptimisticLockException

    async def update_lobby(self, lobby: Lobby, version: int) -> None:
        lobby_data = asdict(lobby)

        result = await self.collection.update_one(
            {"lobby_id": lobby.lobby_id, "version": version},
            {"$set": lobby_data, "$inc": {"version": 1}}
        )
        if result.matched_count == 0:
            raise OptimisticLockException

    async def create_lobby(self, lobby: Lobby) -> None:
        lobby_data = asdict(lobby)
        lobby_data["version"] = 1
        await self.collection.insert_one(lobby_data)

    async def add_player_to_lobby(self, lobby_id: LobbyId, user_id: UserId, version: int) -> None:
        filter_query = {"lobby_id": lobby_id, "version": version}
        update_query = {
            "$addToSet": {"players": user_id},
            "$inc": {"version": 1},
        }
        result = await self.collection.update_one(filter_query, update_query)

        if result.matched_count == 0:
            raise OptimisticLockException

    async def lobby_exists(self, lobby_id: LobbyId) -> bool:
        result = await self.collection.find_one({"lobby_id": lobby_id}, {"_id": 1})
        return result is not None

    async def get_lobby(self, lobby_id: LobbyId) -> (Lobby, int):
        lobby_data = await self.collection.find_one(
            {"lobby_id": lobby_id},
            {"_id": 0}
        )

        if not lobby_data:
            raise LobbyDoesNotExist
        version = lobby_data.get("version")
        lobby_data_without_version = {
            key: value for key, value in lobby_data.items() if key != "version"
        }
        lobby = Lobby(**lobby_data_without_version)
        return lobby, version

    async def get_user_lobby_id(self, user_id: UserId) -> LobbyId | None:
        lobby_id = await self.redis_client.get(UserKeys.user_lobby_id(user_id))
        if not lobby_id:
            return None
        return LobbyId(uuid.UUID(lobby_id))


class LobbyPubSubGateway(LobbyPubSubInterface):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def publish_user_joined_message(self, user_id: UserId, lobby_id: LobbyId) -> None:
        message = LobbyMessage(
            from_lobby_id=lobby_id,
            user_id=user_id,
            action=UserLobbyAction.USER_JOINED_MESSAGE,
            message='User joined lobby',

        )
        logger.debug('LobbyMessage sent: JOIN')
        await self.redis_client.publish(LobbyKeys.lobby_channel(lobby_id), message.model_dump_json(exclude_none=True))

    async def publish_user_left_message(self, user_id: UserId, lobby_id: LobbyId) -> None:
        message = LobbyMessage(
            from_lobby_id=lobby_id,
            user_id=user_id,
            action=UserLobbyAction.USER_LEFT_MESSAGE,
            message='User left lobby',

        )
        logger.debug('LobbyMessage sent: LEFT')
        await self.redis_client.publish(LobbyKeys.lobby_channel(lobby_id), message.model_dump_json(exclude_none=True))

    async def publish_lobby_start_searching(self, lobby_id: LobbyId) -> None:
        message = LobbyMessage(
            from_lobby_id=lobby_id,
            action=LobbyAction.START_SEARCH,
            message='Lobby start searching',
        )
        logger.debug('LobbyMessage sent: START SEARCHING')
        await self.redis_client.publish(LobbyKeys.lobby_channel(lobby_id), message.model_dump_json(exclude_none=True))

    async def publish_lobby_stop_searching(self, lobby_id: LobbyId) -> None:
        message = LobbyMessage(
            from_lobby_id=lobby_id,
            action=LobbyAction.STOP_SEARCH,
            message='Lobby stop searching',
        )
        logger.debug('LobbyMessage sent: STOP SEARCHING')
        await self.redis_client.publish(LobbyKeys.lobby_channel(lobby_id), message.model_dump_json(exclude_none=True))

    async def publish_lobby_match_found(self, lobby_id: LobbyId, match_id: MatchId) -> None:
        message = LobbyMessage(
            from_lobby_id=lobby_id,
            action=LobbyAction.ACCEPT_MATCH,
            message='Lobby match found',
            match_id=match_id,
        )
        await self.redis_client.publish(LobbyKeys.lobby_channel(lobby_id), message.model_dump_json(exclude_none=True))

    async def publish_lobby_user_message(self, user_id: UserId, lobby_id: LobbyId, message: str) -> None:
        message = LobbyMessage(
            user_id=user_id,
            from_lobby_id=lobby_id,
            message=message,
            action=UserLobbyAction.MESSAGE_LOBBY,
        )
        await self.redis_client.publish(LobbyKeys.lobby_channel(lobby_id), message.model_dump_json(exclude_none=True))
