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

    async def player_ready(self, match_id: str, user_id: int) -> DefaultApiResponse:
        acceptance_key: str = LobbyKeys.acceptance(match_id)

        if not await self.match_repository.exists(acceptance_key):
            raise EntityDoesNotExistError('Match')

        await self.match_repository.hset(acceptance_key, str(user_id), json.dumps(True))

        all_ready: bool = await self.match_repository.check_all_ready(acceptance_key)
        await self.match_repository.publish_message(
            action=
        )
        if all_ready:
            asyncio.create_task(
                self.start_match(match_id, acceptance_key)
            )

        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message='Player ready updated'
        )

    async def start_match(self, match_id: str, acceptance_key: str):
        players: list = await self.match_repository.create_match(match_id, acceptance_key)
        set_tasks = [
            self.match_repository.set(UserKeys.user_match_id(uid), match_id)
            for uid in players
        ]
        publish_tasks = [
            self.match_repository.publish_message(
                action=ServiceAction.JOIN_MATCH,
                user_id=uid,
                message=f'Nickname joined the match',
                id=match_id,
                channel_type=ChannelTypes.USER
            )
            for uid in players
        ]

        await asyncio.gather(*set_tasks, *publish_tasks)
