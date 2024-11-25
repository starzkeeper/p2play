from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.core.dependencies import lobby_service
from backend.db.models import User
from backend.services.lobby_service import LobbyService
from backend.utils.auth_dependencies import get_current_user

router_lobby = APIRouter()


@router_lobby.get("/list")
async def list_lobbies(
        service: Annotated[LobbyService, Depends(lobby_service)],
        user: User = Depends(get_current_user),
):
    res = await service.get_all_lobbies()
    return JSONResponse(content=res)


@router_lobby.post("/create")
async def create_lobby(
        service: Annotated[LobbyService, Depends(lobby_service)],
        user: User = Depends(get_current_user),
):
    res = await service.create_lobby()
    return JSONResponse(content=res)


@router_lobby.websocket("/ws/{lobby_id}")
async def connect_lobby(
        websocket: WebSocket,
        lobby_id: str,
        service: LobbyService = Depends(lobby_service),
        user: User = Depends(get_current_user)
):
    try:
        await service.connect_lobby(websocket, user, lobby_id)

        while True:
            data = await websocket.receive_text()
            await service.broadcast_message(lobby_id, data, user)
    except WebSocketDisconnect:
        await service.remove_player(lobby_id, user)
