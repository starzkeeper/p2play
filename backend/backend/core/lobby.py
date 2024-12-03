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
    res = await service.create_lobby(user)
    return JSONResponse(content=res)


@router_lobby.post("/leave")
async def leave_lobby(
        lobby_id: str,
        service: Annotated[LobbyService, Depends(lobby_service)],
        user: User = Depends(get_current_user),
):
    res = await service.remove_player(lobby_id, user)
    return JSONResponse(content=res)


@router_lobby.websocket("/ws")
async def connect_ws(
        websocket: WebSocket,
        service: LobbyService = Depends(lobby_service),
        user: User = Depends(get_current_user),
):
    try:
        await service.connect_lobby(websocket, user)

        while True:
            data = await websocket.receive_json()

            lobby_id = data["lobby_id"]
            message = data["message"]

            await service.broadcast_message(lobby_id, message, user)
    except WebSocketDisconnect:
        pass
