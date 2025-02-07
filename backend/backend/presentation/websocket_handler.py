from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from backend.adapters.pubsub.pubsub import PubSubGateway


class WebSocketHandler:
    def __init__(
            self,
            websocket: WebSocket,
            pubsub_gateway: PubSubGateway,
    ):
        self.websocket = websocket
        self.pubsub_gateway = pubsub_gateway

    async def accept(self):
        await self.websocket.accept()

    async def receive(self):
        try:
            while True:
                data = await self.websocket.receive_text()

        except WebSocketDisconnect:
            await self.pubsub_gateway.stop_listening()
