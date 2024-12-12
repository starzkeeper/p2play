import asyncio
import json

from redis.asyncio.client import PubSub
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.db.models import User
from backend.repositories.common_schema import MessageAction
from backend.repositories.websocket_repository import WebSocketRepository
from backend.schemas.lobby_schema import JoinMessage, LeaveMessage, ChannelTypes, LobbyMessage
from backend.utils.redis_keys import LobbyKeys, MatchKeys, UserKeys


class WebSocketService:
    def __init__(self, websocket_repository: WebSocketRepository) -> None:
        self.websocket_repository = websocket_repository

    async def connect_lobby(self, websocket: WebSocket, user: User):
        task = None
        user_pubsub = None
        try:
            await websocket.accept()

            user_pubsub: PubSub = await self.websocket_repository.subscribe_to(UserKeys.user_channel(user.id))

            lobby_id = await self.websocket_repository.get(UserKeys.user_lobby_id(user.id))
            match_id = await self.websocket_repository.get(UserKeys.user_match_id(user.id))

            if lobby_id:
                await user_pubsub.subscribe(LobbyKeys.lobby_channel(lobby_id))
            if match_id:
                await user_pubsub.subscribe(MatchKeys.match_channel(match_id))

            task = asyncio.create_task(self.listen_channel(user_pubsub, websocket, user.id))

            while True:
                try:
                    data = await websocket.receive_json()

                    message = data["message"]

                    await self.broadcast_message(message, user)
                except WebSocketDisconnect:
                    break
        finally:
            if task:
                task.cancel()
            await user_pubsub.close()

    async def listen_channel(self, pubsub: PubSub, websocket: WebSocket, user_id: int):
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if not message:
                await asyncio.sleep(0.05)
                continue

            message_data = json.loads(message['data'])
            channel_type = message_data.get('type')

            if channel_type == ChannelTypes.USER:
                await self.handle_user_subscriptions(message_data, pubsub)

            # if action in {MessageAction.JOIN, MessageAction.LEAVE} and recipient == Recipient.USER_CHANNEL:
            #     if channel_type == ChannelTypes.LOBBY:
            #         await self.handle_lobby_subscription(message_data, pubsub)
            #     elif channel_type == ChannelTypes.MATCH:
            #         await self.handle_match_subscription(message_data, pubsub)

            await websocket.send_json(message_data)

    async def handle_user_subscriptions(self, message_data: dict, pubsub: PubSub):
        action = message_data.get('action')
        lobby_id = message_data.get('lobby_id')
        match_id = message_data.get('match_id')

        if action == MessageAction.JOIN_LOBBY:
            channel = LobbyKeys.lobby_channel(lobby_id)
            await pubsub.subscribe(channel)
        elif action == MessageAction.LEAVE_LOBBY:
            channel = LobbyKeys.lobby_channel(lobby_id)
            await pubsub.subscribe(channel)
        elif action == MessageAction.JOIN_MATCH:
            channel = MatchKeys.match_channel(match_id)
            await pubsub.subscribe(channel)
        elif action == MessageAction.LEAVE_MATCH:
            channel = MatchKeys.match_channel(match_id)
            await pubsub.subscribe(channel)
        else:
            # Если действие не распознано
            print(f"Unhandled action: {action}")

    # async def handle_match_subscription(self, message_data: JoinMessage | LeaveMessage, pubsub: PubSub):
    #     match_id = message_data.get('match_id')
    #     action = message_data.get('action')
    #     channel = MatchKeys.match_channel(match_id)
    #
    #     if action == MessageAction.JOIN:
    #         await pubsub.subscribe(channel)
    #     elif action == MessageAction.LEAVE:
    #         await pubsub.unsubscribe(channel)

    async def broadcast_message(self, message: str, user: User):
        lobby_id = await self.websocket_repository.get(UserKeys.user_lobby_id(user.id))
        if not lobby_id:
            return

        formatted_message = LobbyMessage(
            user_id=user.id,
            message=message,
            lobby_id=lobby_id
        )

        await self.websocket_repository.publish_message(
            LobbyKeys.lobby_channel(lobby_id),
            formatted_message
        )
