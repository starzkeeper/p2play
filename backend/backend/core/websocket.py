from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket

from backend.core.dependencies import websocket_service
from backend.db.models import User

from backend.services.websocket_service import WebSocketService
from backend.utils.auth_dependencies import get_current_user

router_websocket = APIRouter()


@router_websocket.websocket("/ws")
async def connect_ws(
        websocket: WebSocket,
        service: WebSocketService = Depends(websocket_service),
        user: User = Depends(get_current_user),
):
    await service.connect_lobby(websocket, user)
