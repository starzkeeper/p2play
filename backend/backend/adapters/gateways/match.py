from dataclasses import asdict

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from redis.asyncio import Redis

from backend.application.errors.match import MatchDoesNotExist
from backend.application.match.gateway import MatchSaver, MatchReader
from backend.domain.match.models import MatchId, Match


class MatchGateway(MatchSaver, MatchReader):
    def __init__(self, mongo_db: AsyncDatabase, redis_client: Redis):
        self.collection: AsyncCollection = mongo_db['match']
        self.redis_client = redis_client

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
