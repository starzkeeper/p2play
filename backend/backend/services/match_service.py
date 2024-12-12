import asyncio
import json

from backend.exceptions.exceptions import InvalidOperationError, EntityDoesNotExistError
from backend.repositories.match_repository import MatchRepository
from backend.schemas.lobby_schema import Recipient
from backend.schemas.match_schema import MatchStatus, JoinMatchMessage
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus
from backend.utils.redis_keys import MatchKeys, UserKeys, LobbyKeys


class MatchService:
    def __init__(self, match_repository: MatchRepository) -> None:
        self.match_repository = match_repository

    async def player_ready(self, match_id: str, user_id: int) -> DefaultApiResponse:
        acceptance_key = LobbyKeys.acceptance(match_id)

        if not await self.match_repository.exists(acceptance_key):
            raise EntityDoesNotExistError('Match')



        if all_ready:
            players = acceptance.keys()
            await self.match_repository.create_match(match_id, )
            set_tasks = [
                self.match_repository.set(UserKeys.user_match_id(uid), match_id)
                for uid in players
            ]
            publish_tasks = [
                self.match_repository.publish_message(
                    channel_name=UserKeys.user_channel(uid),
                    message=JoinMatchMessage(match_id=match_id, message='Joined match'),
                    recipient=Recipient.USER_CHANNEL
                )
                for uid in players
            ]
            await asyncio.gather(*set_tasks, *publish_tasks)

        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message='Player ready updated'
        )
