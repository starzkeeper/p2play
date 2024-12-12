import asyncio

from backend.db.models import User
from backend.exceptions.exceptions import EntityDoesNotExistError, EntityAlreadyExistsError, InvalidOperationError
from backend.repositories.common_schema import ChannelTypes
from backend.repositories.lobby_repository import LobbyRepository
from backend.schemas.lobby_schema import JoinMessage, LeaveMessage, WaitAcceptanceMatchMessage, LobbyStatus
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus
from backend.utils.redis_keys import LobbyKeys, UserKeys


class LobbyService:
    def __init__(self, lobby_repository: LobbyRepository) -> None:
        self.lobby_repository = lobby_repository

    async def create_lobby(self, user: User):
        existed_lobby = await self.lobby_repository.exists(UserKeys.user_lobby_id(user.id))
        if existed_lobby:
            await self.remove_player(user)

        lobby_id = await self.lobby_repository.create_lobby(user.id)
        formatted_message = JoinMessage(
            user_id=user.id,
            lobby_id=lobby_id,
            message=f'Nickname joined the lobby',
            type=ChannelTypes.USER
        )

        await self.lobby_repository.set(UserKeys.user_lobby_id(user.id), lobby_id)
        await self.lobby_repository.publish_message(
            UserKeys.user_channel(user.id), formatted_message)

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

        formatted_message_user = LeaveMessage(
            user_id=user.id,
            message=f'{user.id} left the lobby',
            lobby_id=lobby_id,
        )

        await self.lobby_repository.publish_message(
            UserKeys.user_channel(user.id),
            formatted_message_user
        )
        await self.lobby_repository.publish_message(
            LobbyKeys.lobby_channel(lobby_id),
            formatted_message_lobby

        )
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
        lobby: bool = await self.lobby_repository.exists(LobbyKeys.lobby(lobby_id))
        if not lobby:
            raise EntityDoesNotExistError('Lobby')

        existed_lobby: str = await self.lobby_repository.get(UserKeys.user_lobby_id(user.id))

        if existed_lobby == lobby_id:
            raise EntityAlreadyExistsError

        if existed_lobby:
            await self.remove_player(user)

        await self.lobby_repository.add_player(lobby_id, user.id)

        formatted_message = JoinMessage(
            user_id=user.id,
            lobby_id=lobby_id,
            message=f'Nickname joined the lobby'
        )

        await self.lobby_repository.publish_message(UserKeys.user_channel(user.id),
                                                    formatted_message,
                                                    )
        await self.lobby_repository.publish_message(LobbyKeys.lobby_channel(lobby_id),
                                                    formatted_message,
                                                    )

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

    async def add_to_queue(self, user_id: int):
        lobby_id = await self.lobby_repository.get(UserKeys.user_lobby_id(user_id))
        if not lobby_id:
            raise InvalidOperationError
        lobby = await self.lobby_repository.hgetall(LobbyKeys.lobby(lobby_id))

        owner_id = lobby.get('owner_id')
        if int(owner_id) != int(user_id):
            raise InvalidOperationError

        await self.lobby_repository.add_to_queue(lobby_id)
        asyncio.create_task(self.try_create_match())

        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message='Lobby added to queue'
        )

    async def try_create_match(self):
        # TODO: algorithm, condition race fix, search missing players
        queue = await self.lobby_repository.get_queue()
        if len(queue) < 2:
            return

        lobby_id_1, lobby_id_2 = queue[0], queue[1]
        await self.lobby_repository.lrem("matchmaking_queue", 0, lobby_id_1)
        await self.lobby_repository.lrem("matchmaking_queue", 0, lobby_id_2)

        match_id, all_players = await self.lobby_repository.create_acceptance(
            lobby_id_1,
            lobby_id_2
        )

        notification_message = WaitAcceptanceMatchMessage(
            match_id=match_id,
            message='Match created',
        )

        user_join_messages = [
            self.lobby_repository.publish_message(
                UserKeys.user_channel(uid),
                notification_message
            )
            for uid in all_players
        ]
        await asyncio.gather(*user_join_messages)
