import asyncio
import json
from typing import Optional

from fastapi import HTTPException
from redis.asyncio.client import PubSub
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.db.models import User
from backend.repositories.lobby_repository import LobbyRepository
from backend.schemas.lobby_schema import LobbyMessage, MessageAction, JoinMessage
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus


class LobbyService:
    def __init__(self, lobby_repository: LobbyRepository) -> None:
        self.lobby_repository = lobby_repository
        self.tasks = {}

    async def create_lobby(self, user: User):
        existed_lobby = await self.lobby_repository.get(f'user:{user.id}:lobby_id')
        if existed_lobby:
            await self.remove_player(existed_lobby, user)

        lobby_id = await self.lobby_repository.create_lobby(user.id)
        formatted_message = JoinMessage(
            message=f'{user.id} joined the lobby',
            lobby_id=lobby_id
        )

        await self.lobby_repository.set(f'user:{user.id}:lobby_id', lobby_id)
        await self.lobby_repository.publish_message(f'user_channel:{user.id}', formatted_message)

        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=lobby_id
        )

    async def connect_lobby(self, websocket: WebSocket, user: User):
        await websocket.accept()

        user_pubsub: PubSub = await self.lobby_repository.subscribe_to(f'user_channel:{user.id}')

        lobby_id = await self.lobby_repository.get(f'user:{user.id}:lobby_id')
        if lobby_id:
            await user_pubsub.subscribe(f'lobby_channel:{lobby_id}')

        asyncio.create_task(self.listen_channel(user_pubsub, websocket, user.id))

    async def listen_channel(self, pubsub: PubSub, websocket: WebSocket, user_id: int):
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if not message:
                await asyncio.sleep(0.1)
                continue

            message_data = json.loads(message['data'])
            action = message_data.get('action')
            if action in {MessageAction.JOIN, MessageAction.LEAVE}:
                await self.handle_lobby_subscription(action, user_id, pubsub)

            await websocket.send_json(message_data)

    async def handle_lobby_subscription(self, action: MessageAction, user_id: int, pubsub: PubSub):
        lobby_id = await self.lobby_repository.get(f'user:{user_id}:lobby_id')
        channel = f'lobby_channel:{lobby_id}'

        if action == MessageAction.JOIN:
            await pubsub.subscribe(channel)
        elif action == MessageAction.LEAVE:
            await pubsub.unsubscribe(channel)

    async def broadcast_message(self, lobby_id: str, message: str, user: User):
        formatted_message = LobbyMessage(
            user_id=user.id,
            message=message
        )

        await self.lobby_repository.publish_message(f"lobby_channel:{lobby_id}", formatted_message)

    async def remove_player(self, lobby_id: int, user: User):
        await self.lobby_repository.remove_player(lobby_id, user.id)
        formatted_message = LobbyMessage(
            user_id=user.id,
            action=MessageAction.MESSAGE,
            message=f'{user.id} left the lobby'
        )

        await self.lobby_repository.publish_message(f"lobby_channel_{lobby_id}", formatted_message)
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

    async def lobby_and_player_check(self, lobby_id: int, user_id: int):
        lobby_exists: bool = await self.lobby_repository.get_lobby(lobby_id)
        if not lobby_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lobby not founded')

        lobby = await self.lobby_repository.is_user_in_lobby(user_id)
        if lobby and lobby != lobby_id:
            await self.lobby_repository.delete_user_lobby_key(user_id)
        return
