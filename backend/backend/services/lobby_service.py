import asyncio

from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.db.models import User
from backend.repositories.lobby_repository import LobbyRepository
from backend.schemas.lobby_schema import LobbyMessage, MessageAction
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus


class LobbyService:
    def __init__(self, lobby_repository: LobbyRepository) -> None:
        self.lobby_repository = lobby_repository

    async def create_lobby(self):
        lobby_id = await self.lobby_repository.create_lobby()
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=lobby_id
        )

    async def connect_lobby(self, websocket: WebSocket, user: User, lobby_id: str):
        await websocket.accept()

        lobby_exists: bool = await self.lobby_repository.get_lobby(lobby_id)
        if not lobby_exists:
            print('no lobby')
            await websocket.close()
            raise WebSocketDisconnect

        if not await self.lobby_repository.add_player(lobby_id, user.id):
            print('not adding player')
            await websocket.close()
            raise WebSocketDisconnect

        pubsub = await self.lobby_repository.subscribe_to_lobby(lobby_id)

        formatted_message = LobbyMessage(
            user_id=user.id,
            action=MessageAction.JOIN,
            message=f'{user.id} joined the lobby.'
        )
        await self.lobby_repository.publish_message(lobby_id, formatted_message)

        asyncio.create_task(self.lobby_repository.read_pubsub_messages(pubsub, websocket))
        return True

    async def broadcast_message(self, lobby_id: str, message: str, user: User):
        formatted_message = LobbyMessage(
            user_id=user.id,
            message=message
        )

        await self.lobby_repository.publish_message(lobby_id, formatted_message)

    async def remove_player(self, lobby_id: int, user: User):
        await self.lobby_repository.remove_player(lobby_id, user.id)
        formatted_message = LobbyMessage(
            user_id=user.id,
            action=MessageAction.MESSAGE,
            message=f'{user.id} leaved the lobby'
        )
        await self.lobby_repository.publish_message(lobby_id, formatted_message)

    async def get_all_lobbies(self):
        # TODO: поиск по рейтингу
        lobbies = await self.lobby_repository.all_lobbies()
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=lobbies
        )
