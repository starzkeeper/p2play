import asyncio
import json
import logging

from redis.asyncio.client import PubSub
from fastapi import WebSocket

from backend.adapters.messages.message import ChannelTypes
from backend.adapters.persistence.redis_keys import UserKeys, LobbyKeys, MatchKeys
from backend.adapters.pubsub.message_handlers.registry import CHANNEL_HANDLERS
from backend.application.websocket.gateway import PubSubInterface
from backend.domain.lobby.models import MatchId, LobbyId
from backend.domain.user.models import UserId

logger = logging.getLogger('p2play')


class PubSubGateway(PubSubInterface):

    def __init__(
            self,
            pubsub: PubSub,
            websocket: WebSocket
    ):
        self.pubsub: PubSub = pubsub
        self.websocket: WebSocket = websocket
        self.listen_task: asyncio.Task | None = None

    async def subscribe_user_channel(self, user_id: UserId) -> None:
        await self.pubsub.subscribe(UserKeys.user_channel(str(user_id)))
        logger.debug(f"Subscribed to user channel: {self.pubsub.channels}")

    async def unsubscribe_user_channel(self, user_id: UserId) -> None:
        await self.pubsub.unsubscribe(UserKeys.user_channel(str(user_id)))
        logger.debug(f"Unsubscribed from user channel: {self.pubsub.channels}")

    async def subscribe_lobby_channel(self, lobby_id: LobbyId) -> None:
        await self.pubsub.subscribe(LobbyKeys.lobby_channel(str(lobby_id)))
        logger.debug(f"Subscribed to lobby channel: {LobbyKeys.lobby_channel(str(lobby_id))}")

    async def unsubscribe_lobby_channel(self, lobby_id: LobbyId) -> None:
        await self.pubsub.unsubscribe(LobbyKeys.lobby_channel(str(lobby_id)))
        logger.debug(f"Unsubscribed from lobby channel: {LobbyKeys.lobby_channel(str(lobby_id))}")

    async def subscribe_match_channel(self, match_id: MatchId) -> None:
        await self.pubsub.subscribe(MatchKeys.match_channel(str(match_id)))
        logger.debug(f"Subscribed to match channel: {MatchKeys.match_channel(str(match_id))}")

    async def unsubscribe_match_channel(self, match_id: MatchId) -> None:
        await self.pubsub.unsubscribe(MatchKeys.match_channel(str(match_id)))
        logger.debug(f"Unsubscribed from match channel: {MatchKeys.match_channel(str(match_id))}")

    async def listen_channel(self) -> None:
        while True:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            except RuntimeError as e:
                break
            if not message:
                await asyncio.sleep(0.05)
                continue

            try:
                message_data = json.loads(message['data'])
            except json.decoder.JSONDecodeError as e:
                logger.error(f"JSONDecodeError: {e} for data: {message['data']}")
                continue

            channel_type = message_data.get('type')
            logger.debug(f'{message_data}')
            handler = CHANNEL_HANDLERS.get(ChannelTypes(channel_type))
            logger.debug(f'handler: {handler}')
            if handler:
                await handler(message_data, self.pubsub)
            try:
                await self.websocket.send_json(message_data)
            except Exception as e:
                logger.error(f"Error sending message through websocket: {e}")
                break

    async def start_listening(self) -> None:
        self.listen_task = asyncio.create_task(self.listen_channel())

    async def stop_listening(self) -> None:
        if self.listen_task:
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                logger.debug("Listening task cancelled successfully")
            self.listen_task = None
        await self.pubsub.close()
        logger.debug("PubSub closed")
