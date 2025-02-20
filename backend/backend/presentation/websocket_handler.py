import uuid

from dishka import AsyncContainer
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from backend.adapters.gateways.lobby import LobbyPubSubGateway
from backend.adapters.messages.message import ChannelTypes
from backend.adapters.pubsub.pubsub import PubSubGateway
from backend.application.lobby.gateway import LobbyReader, LobbyPubSubInterface
from backend.application.lobby.interactors.broadcast_lobby_message import BroadcastLobbyMessage, \
    BroadcastLobbyMessageInputDTO
from backend.application.match.interactors.broadcast_ban_map_message import BroadcastBanMapMessage, \
    BroadcastBanMapMessageInputDTO
from backend.domain.lobby.models import LobbyId, MatchId
from backend.domain.match.models import MatchAction
from backend.domain.user.models import UserId


class WebSocketHandler:
    def __init__(
            self,
            websocket: WebSocket,
            pubsub_gateway: PubSubGateway,
            container: AsyncContainer,
    ):
        self.websocket = websocket
        self.pubsub_gateway = pubsub_gateway
        self.container = container

    async def accept(self):
        await self.websocket.accept()

    async def receive(self, user_id: UserId):
        try:
            while True:
                data: dict = await self.websocket.receive_json()
                channel_type: ChannelTypes = data.get("channel")
                message = data.get("message")
                if channel_type == ChannelTypes.LOBBY:
                    async with self.container() as request_container:
                        broadcast_message: BroadcastLobbyMessage = await request_container.get(BroadcastLobbyMessage)
                        await broadcast_message(
                            BroadcastLobbyMessageInputDTO(
                                user_id=user_id,
                                message=message
                            )
                        )
                elif channel_type == ChannelTypes.MATCH:
                    action: MatchAction = data.get("action")
                    match_id: str = data.get("match_id")
                    if action is not None and match_id is not None:
                        match_id: MatchId = MatchId(uuid.UUID(match_id))
                        async with self.container() as request_container:
                            broadcast_message: BroadcastBanMapMessage = await request_container.get(BroadcastBanMapMessage)
                            await broadcast_message(
                                BroadcastBanMapMessageInputDTO(
                                    user_id=user_id,
                                    match_id=match_id,
                                    action=action
                                )
                            )

        except WebSocketDisconnect:
            await self.pubsub_gateway.stop_listening()
