import asyncio

from dishka import FromDishka, AsyncContainer
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, WebSocket

from backend.application.common.id_provider import IdProvider
from backend.application.websocket.interactors.connect_websocket import ConnectWebsocket
from backend.presentation.websocket_handler import WebSocketHandler

router_websocket = APIRouter()


@router_websocket.websocket("/ws")
@inject
async def connect_ws(
        websocket: WebSocket,  # dont use
        container: FromDishka[AsyncContainer],
        websocket_handler: FromDishka[WebSocketHandler]
):
    await websocket_handler.accept()
    async with container() as request_container:
        id_provider: IdProvider = await request_container.get(IdProvider)
        user = await id_provider.get_current_user()
        service: ConnectWebsocket = await request_container.get(ConnectWebsocket)
        await service(user.id)
    await websocket_handler.receive()
