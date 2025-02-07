from dataclasses import asdict
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from backend.application.match.interactors.get_maps import GetMaps
from backend.application.match.interactors.get_match_by_id import GetMatchById
from backend.domain.lobby.models import MatchId

router_match = APIRouter(route_class=DishkaRoute)


@router_match.get('/all-maps')
async def get_maps(
        service: FromDishka[GetMaps],
):
    res = await service()
    return {'result': asdict(res)}


@router_match.get('/search-match')
async def get_match(
        match_id: MatchId,
        service: FromDishka[GetMatchById]
):
    res = await service(match_id)
    return {'result': asdict(res)}
