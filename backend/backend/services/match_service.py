import asyncio
import json

from backend.repositories.match_repository import MatchRepository
from backend.schemas.lobby_schema import Recipient
from backend.schemas.match_schema import MatchStatus, JoinMatchMessage
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus
from backend.utils.redis_keys import MatchKeys, UserKeys


class MatchService:
    def __init__(self, match_repository: MatchRepository) -> None:
        self.match_repository = match_repository

    async def player_ready(self, match_id: str, user_id: int) -> DefaultApiResponse:
        match_key = MatchKeys.match(match_id)
        acceptance: dict[str, bool] = await self.match_repository.hget(match_key, 'acceptance')
        if not acceptance:
            return DefaultApiResponse(
                status=ApiStatus.ERROR,
                message='Invalid match data'
            )

        user_id_str = str(user_id)
        if user_id_str not in acceptance:
            return DefaultApiResponse(
                status=ApiStatus.ERROR,
                message='User not in this match'
            )

        acceptance[user_id_str] = True

        data = {
            'acceptance': json.dumps(acceptance)
        }
        all_ready = all(acceptance.values())

        if all_ready:
            data['status'] = MatchStatus.PREPARATION

        await self.match_repository.hset(match_key, mapping=data)

        if all_ready:
            players = acceptance.keys()
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
