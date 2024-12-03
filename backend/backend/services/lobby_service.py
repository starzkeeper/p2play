import asyncio
import json

from redis.asyncio.client import PubSub
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.db.models import User
from backend.repositories.lobby_repository import LobbyRepository
from backend.schemas.lobby_schema import LobbyMessage, MessageAction, JoinMessage, Sender
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus


class LobbyService:
    def __init__(self, lobby_repository: LobbyRepository) -> None:
        self.lobby_repository = lobby_repository
        self.tasks = {}

    async def create_lobby(self, user: User):
        existed_lobby = await self.lobby_repository.exists(f'user:{user.id}:lobby_id')
        if existed_lobby:
            await self.remove_player(user)

        lobby_id = await self.lobby_repository.create_lobby(user.id)
        formatted_message = JoinMessage(
            user_id=user.id,
            lobby_id=lobby_id,
            message=f'Nickname joined the lobby'
        )

        await self.lobby_repository.set(f'user:{user.id}:lobby_id', lobby_id)
        await self.lobby_repository.publish_message(
            f'user_channel:{user.id}', formatted_message, Sender.USER_CHANNEL)

        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=lobby_id
        )

    async def connect_lobby(self, websocket: WebSocket, user: User):
        task = None
        user_pubsub = None
        try:
            await websocket.accept()

            user_pubsub: PubSub = await self.lobby_repository.subscribe_to(f'user_channel:{user.id}')

            lobby_id = await self.lobby_repository.get(f'user:{user.id}:lobby_id')
            if lobby_id:
                await user_pubsub.subscribe(f'lobby_channel:{lobby_id}')

            task = asyncio.create_task(self.listen_channel(user_pubsub, websocket))

            while True:
                try:
                    data = await websocket.receive_json()

                    message = data["message"]

                    await self.broadcast_message(message, user)
                except WebSocketDisconnect:
                    break
        except Exception as e:
            print(f'Unexpected error: {e}')
        finally:
            if task:
                task.cancel()
            await user_pubsub.close()

    async def listen_channel(self, pubsub: PubSub, websocket: WebSocket):
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if not message:
                await asyncio.sleep(0.05)
                continue

            message_data = json.loads(message['data'])
            action = message_data.get('action')
            if action in {MessageAction.JOIN, MessageAction.LEAVE}:
                await self.handle_lobby_subscription(message_data, pubsub)

            await websocket.send_json(message_data)

    async def handle_lobby_subscription(self, message_data: JoinMessage, pubsub: PubSub):
        lobby_id = message_data.get('lobby_id')
        action = message_data.get('action')
        channel = f'lobby_channel:{lobby_id}'

        if action == MessageAction.JOIN:
            await pubsub.subscribe(channel)
        elif action == MessageAction.LEAVE:
            await pubsub.unsubscribe(channel)

    async def broadcast_message(self, message: str, user: User):
        lobby_id = await self.lobby_repository.get(f'user:{user.id}:lobby_id')
        if not lobby_id:
            return

        formatted_message = LobbyMessage(
            user_id=user.id,
            message=message,
            lobby_id=lobby_id
        )

        await self.lobby_repository.publish_message(f"lobby_channel:{lobby_id}", formatted_message,
                                                    Sender.LOBBY_CHANNEL)

    async def remove_player(self, user: User):
        lobby_id = await self.lobby_repository.get(f'user:{user.id}:lobby_id')
        if not lobby_id:
            return DefaultApiResponse(
                status=ApiStatus.SUCCESS,
                message=f'{user.id} left the lobby.'
            )

        await self.lobby_repository.remove_player(lobby_id, user.id)
        formatted_message = LobbyMessage(
            user_id=user.id,
            action=MessageAction.MESSAGE,
            message=f'{user.id} left the lobby',
            lobby_id=lobby_id
        )

        await self.lobby_repository.publish_message(f"lobby_channel:{lobby_id}", formatted_message,
                                                    Sender.LOBBY_CHANNEL)
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
        lobby = await self.lobby_repository.hgetall(f'lobby_{lobby_id}')
        if not lobby:
            return DefaultApiResponse(
                status=ApiStatus.ERROR,
                message=f'Lobby {lobby_id} does not exist'
            )

        existed_lobby = await self.lobby_repository.exists(f'user:{user.id}:lobby_id')
        if existed_lobby:
            await self.remove_player(user)

        await self.lobby_repository.add_player(lobby_id, user.id)

        formatted_message = JoinMessage(
            user_id=user.id,
            lobby_id=lobby_id,
            message=f'Nickname joined the lobby'
        )
        await self.lobby_repository.publish_message(f'lobby_channel:{lobby_id}', formatted_message,
                                                    Sender.LOBBY_CHANNEL)
        await self.lobby_repository.publish_message(f'user_channel:{user.id}', formatted_message,
                                                    Sender.USER_CHANNEL)
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=f'Nickname joined the lobby.'
        )
