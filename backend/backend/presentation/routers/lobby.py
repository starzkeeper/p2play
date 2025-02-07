from dataclasses import asdict

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from backend.application.lobby.interactors.create_lobby import CreateLobby
from backend.application.lobby.interactors.get_lobby_by_uid import GetUserLobby
from backend.application.lobby.interactors.join_lobby import JoinLobby, JoinLobbyDTO
from backend.application.lobby.interactors.player_ready import PlayerReady, PlayerReadyDTO
from backend.application.lobby.interactors.remove_player import RemovePlayer
from backend.application.lobby.interactors.start_searching import StartSearching
from backend.application.lobby.interactors.stop_searching import StopSearching

router_lobby = APIRouter(route_class=DishkaRoute)


@router_lobby.post("/create")
async def create_lobby(
        service: FromDishka[CreateLobby],
):
    lobby_id = await service()
    return {'result': lobby_id}


@router_lobby.post("/leave")
async def leave_lobby(
        service: FromDishka[RemovePlayer],
):
    res = await service()
    return {'result': 'user left'}


@router_lobby.post("/join")
async def join_lobby(
        service: FromDishka[JoinLobby],
        lobby_data: JoinLobbyDTO
):
    res = await service(lobby_data)
    return {'result': 'user joined lobby'}


@router_lobby.get("/search-user-lobby")
async def get_user_lobby(
        service: FromDishka[GetUserLobby]
):
    res = await service()
    if res:
        res = asdict(res)
    return {'result': res}


@router_lobby.post("/start-matchmaking")
async def start_matchmaking(
        service: FromDishka[StartSearching]
):
    res = await service()
    return {'result': 'lobby start searching'}


@router_lobby.get("/stop-matchmaking")
async def stop_matchmaking(
        service: FromDishka[StopSearching]
):
    res = await service()
    return {'result': 'lobby stop searching'}


@router_lobby.post("/ready")
async def player_ready(
        data: PlayerReadyDTO,
        service: FromDishka[PlayerReady]
):
    res = await service(data)
    return {'result': 'player ready'}
