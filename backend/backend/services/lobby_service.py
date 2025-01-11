import asyncio
import logging

from backend.db.models import User
from backend.repositories.lobby_repository import LobbyRepository
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus
from backend.utils.redis_keys import LobbyKeys, UserKeys

logger = logging.getLogger('p2play')


class LobbyService:
    def __init__(self, lobby_repository: LobbyRepository) -> None:
        self.lobby_repository = lobby_repository

    async def create_lobby(self, user: User):
        if await self.lobby_repository.exists(UserKeys.user_lobby_id(user.id)):
            logger.debug('Lobby exist')
            await self.remove_player(user)
        lobby_id = await self.lobby_repository.create_lobby(user.id)
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=lobby_id
        )

    async def remove_player(self, user: User):
        lobby_id = await self.lobby_repository.get(UserKeys.user_lobby_id(user.id))
        if not lobby_id:
            return DefaultApiResponse(
                status=ApiStatus.SUCCESS,
                message=f'{user.id} left the lobby.'
            )
        await self.lobby_repository.remove_player(lobby_id, user.id)
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=f'{user.id} left the lobby.'
        )

    async def get_all_lobbies(self):
        # TODO: поиск по рейтингу
        lobbies = await self.lobby_repository.all_lobbies()
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=lobbies
        )

    async def join_lobby(self, lobby_id: str, user: User):
        await self.lobby_repository.add_player(lobby_id, user.id)

        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=f'Nickname joined the lobby.'
        )

    async def search_lobby(self, user_id: int):
        lobby_id = await self.lobby_repository.get(UserKeys.user_lobby_id(user_id))
        if not lobby_id:
            return DefaultApiResponse(
                status=ApiStatus.SUCCESS,
                message=None
            )

        lobby = await self.lobby_repository.hgetall(LobbyKeys.lobby(lobby_id))
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=lobby
        )

    async def start_searching_match(self, user_id: int):
        await self.lobby_repository.add_to_queue(user_id)

        asyncio.create_task(self.try_create_acceptance())

        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message='Lobby added to queue'
        )

    async def try_create_acceptance(self):
        await self.lobby_repository.create_acceptance()

    async def player_ready(self, match_id: str, user_id: int) -> DefaultApiResponse:
        await self.lobby_repository.player_ready(match_id, user_id)

        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message='Player ready updated'
        )
