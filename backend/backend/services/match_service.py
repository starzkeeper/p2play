import asyncio
import json

from backend.exceptions.exceptions import InvalidOperationError, EntityDoesNotExistError
from backend.repositories.match_repository import MatchRepository
from backend.schemas.common_schema import ChannelTypes
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus
from backend.utils.redis_keys import MatchKeys, UserKeys, LobbyKeys


class MatchService:
    def __init__(self, match_repository: MatchRepository) -> None:
        self.match_repository = match_repository

