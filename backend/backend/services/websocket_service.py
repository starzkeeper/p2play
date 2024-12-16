import asyncio
import json
import logging

from redis.asyncio.client import PubSub
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.db.models import User
from backend.repositories.websocket_repository import WebSocketRepository
from backend.schemas.common_schema import ChannelTypes
from backend.utils.message_handlers.registry import CHANNEL_HANDLERS
from backend.utils.redis_keys import LobbyKeys, MatchKeys, UserKeys

logger = logging.getLogger('p2play')


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
            logger.debug(f'{message_data}')

            handler = CHANNEL_HANDLERS.get(ChannelTypes(channel_type))
            if handler:
                await handler(message_data, pubsub)

            await websocket.send_json(message_data)

    async def broadcast_message(self, message: str, user: User):
        logger.debug('Broadcast message')
        lobby_id = await self.websocket_repository.get(UserKeys.user_lobby_id(user.id))
        if not lobby_id:
            return

        await self.websocket_repository.publish_message(
            action=MessageAction.MESSAGE_LOBBY,
            user_id=user.id,
            message=message,
            id=lobby_id,
            channel_type=ChannelTypes.LOBBY
        )
