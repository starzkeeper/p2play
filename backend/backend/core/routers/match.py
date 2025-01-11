from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from backend.core.dependencies import match_service
from backend.db.models import User
from backend.schemas.game_schema import Map
from backend.services.match_service import MatchService
from backend.utils.auth_dependencies import get_current_user

router_match = APIRouter()


@router_match.get('/all-maps')
async def get_maps(
        service: Annotated[MatchService, Depends(match_service)],
):
    res = await service.get_all_maps()
    return JSONResponse(content={'result': res})


@router_match.get('/search-user-match')
async def get_user_match(
        service: Annotated[MatchService, Depends(match_service)],
        user: User = Depends(get_current_user),
):
    res = await service.get_match(user.id)
    return JSONResponse(content={'result': res})


@router_match.post('/ban-map')
async def ban_map(
        map_name: Map,
        service: Annotated[MatchService, Depends(match_service)],
        user: User = Depends(get_current_user),
):
    res = await service.ban_map(user, map_name)
    return JSONResponse(content={'result': res})
