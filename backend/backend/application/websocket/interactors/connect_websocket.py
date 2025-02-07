import asyncio
import logging

from backend.application.common.interactor import Interactor
from backend.application.lobby.gateway import LobbyReader
from backend.application.websocket.gateway import PubSubInterface
from backend.domain.user.models import UserId

logger = logging.getLogger('p2play')


class ConnectWebsocket(Interactor[UserId, None]):
    def __init__(
            self,
            lobby_reader: LobbyReader,
            pubsub_gateway: PubSubInterface
    ):
        self.lobby_reader = lobby_reader
        self.pubsub_gateway = pubsub_gateway

    async def __call__(self, data: UserId) -> None:
        await self.pubsub_gateway.subscribe_user_channel(data)
        task = asyncio.create_task(self.pubsub_gateway.listen_channel())
        lobby_id = await self.lobby_reader.get_user_lobby_id(data)
        if lobby_id:
            lobby, version = await self.lobby_reader.get_lobby(lobby_id)
            await self.pubsub_gateway.subscribe_lobby_channel(lobby_id)

            if lobby.match_id:
                await self.pubsub_gateway.subscribe_match_channel(lobby.match_id)
        logger.debug('websocket connected')


