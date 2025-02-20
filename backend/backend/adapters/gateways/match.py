import json
import uuid
from dataclasses import asdict

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from redis.asyncio import Redis

from backend.adapters.messages.lobby import AcceptanceMessage
from backend.adapters.messages.match import MatchMessage
from backend.adapters.persistence.redis_keys import LobbyKeys, MatchKeys
from backend.application.errors.match import MatchDoesNotExist
from backend.application.match.gateway import MatchSaver, MatchReader, MatchPubSubInterface
from backend.domain.lobby.models import LobbyId, AcceptanceAction
from backend.domain.match.models import MatchId, Match, MatchAction
from backend.domain.user.models import UserId


class MatchGateway(MatchSaver, MatchReader):
    def __init__(self, mongo_db: AsyncDatabase, redis_client: Redis):
        self.collection: AsyncCollection = mongo_db['match']
        self.redis_client = redis_client

    async def create_acceptance(self, match_id: MatchId, acceptance: dict) -> None:
        # ttl = 10 * 60
        await self.redis_client.hset(LobbyKeys.acceptance(match_id), mapping=acceptance)
        # await self.redis_client.expire(LobbyKeys.acceptance(match_id), ttl)

    async def update_acceptance(self, user_id: UserId, match_id: MatchId) -> None:
        await self.redis_client.hset(LobbyKeys.acceptance(match_id), str(user_id), json.dumps(True))

    async def acceptance_exists(self, acceptance_id: LobbyId) -> bool:
        return await self.redis_client.exists(LobbyKeys.acceptance(acceptance_id))

    async def check_all_ready(self, acceptance_id: str) -> bool:
        acceptance = await self.redis_client.hvals(LobbyKeys.acceptance(acceptance_id))
        print(acceptance)
        return all(json.loads(value) for value in acceptance)

    async def get_acceptance_meta(self, acceptance_id: str) -> tuple[LobbyId, LobbyId]:
        result = await self.redis_client.hgetall(LobbyKeys.acceptance_meta(acceptance_id))
        lobby_id_1, lobby_id_2 = LobbyId(uuid.UUID(result['lobby_id_1'])), LobbyId(uuid.UUID(result['lobby_id_2']))
        return lobby_id_1, lobby_id_2

    async def create_acceptance_meta(self, match_id: MatchId, lobby_id_1: LobbyId, lobby_id_2: LobbyId) -> None:
        acceptance_meta = {
            "match_id": str(match_id),
            "lobby_id_1": str(lobby_id_1),
            "lobby_id_2": str(lobby_id_2)
        }
        await self.redis_client.hset(LobbyKeys.acceptance_meta(match_id), mapping=acceptance_meta)

    async def create_match(self, match: Match) -> None:
        match_data = asdict(match)
        match_data["version"] = 1
        await self.collection.insert_one(match_data)

    async def get_match(self, match_id: MatchId) -> Match:
        match_data = await self.collection.find_one(
            {"match_id": match_id},
            {"_id": 0}
        )
        if not match_data:
            raise MatchDoesNotExist
        version = match_data.get("version")
        match_data_without_version = {
            key: value for key, value in match_data.items() if key != "version"
        }
        match = Match(**match_data_without_version)
        return match, version


class MatchPubSubGateway(MatchPubSubInterface):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def publish_lobby_match_found(self, lobby_id: LobbyId, match_id: MatchId) -> None:
        message = AcceptanceMessage(
            from_lobby_id=lobby_id,
            action=AcceptanceAction.JOIN_MATCH,
            message='Lobby match found',
            match_id=match_id,
        )
        await self.redis_client.publish(LobbyKeys.lobby_channel(lobby_id),
                                        message.model_dump_json(exclude_none=True))

    async def publish_match_preparation_started(self, match_id: MatchId) -> None:
        message = MatchMessage(
            from_match_id=match_id,
            action=MatchAction.MATCH_PREPARATION_STARTED,
            message='Match preparation started',
        )
        await self.redis_client.publish(MatchKeys.match_channel(match_id),
                                        message.model_dump_json(exclude_none=True))

    async def publish_match_user_ban_map(self, match_id: MatchId) -> None:
        message = MatchMessage(
            from_match_id=match_id,
            action=MatchAction.BAN_MAP,
        )
        await self.redis_client.publish(MatchKeys.match_channel(match_id),
                                        message.model_dump_json(exclude_none=True))
