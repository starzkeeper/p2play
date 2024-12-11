from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket

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
    return JSONResponse(content={'result': res})


@router_lobby.post("/create")
async def create_lobby(
        service: Annotated[LobbyService, Depends(lobby_service)],
        user: User = Depends(get_current_user),
):
    res = await service.create_lobby(user)
    return JSONResponse(content={'result': res})


@router_lobby.post("/leave")
async def leave_lobby(
        service: Annotated[LobbyService, Depends(lobby_service)],
        user: User = Depends(get_current_user),
):
    res = await service.remove_player(user)
    return JSONResponse(content={'result': res})


@router_lobby.post("/join")
async def join_lobby(
        lobby_id: str,
        service: Annotated[LobbyService, Depends(lobby_service)],
        user: User = Depends(get_current_user),
):
    res = await service.join_lobby(lobby_id, user)
    return JSONResponse(content={'result': res})


@router_lobby.get("/search-user-lobby")
async def search_user_lobby(
        service: Annotated[LobbyService, Depends(lobby_service)],
        user: User = Depends(get_current_user),
):
    res = await service.search_lobby(user.id)
    return JSONResponse(content={'result': res})


@router_lobby.post("/start-matchmaking")
async def start_matchmaking(
        service: Annotated[LobbyService, Depends(lobby_service)],
        user: User = Depends(get_current_user),
):
    res = await service.add_to_queue(user.id)
    return JSONResponse(content={'result': res})
