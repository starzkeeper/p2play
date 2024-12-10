from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from backend.core.dependencies import match_service
from backend.db.models import User
from backend.services.match_service import MatchService
from backend.utils.auth_dependencies import get_current_user

router_match = APIRouter()


@router_match.post("/{match_id}/ready")
async def player_ready(
        match_id: str,
        service: Annotated[MatchService, Depends(match_service)],
        user: User = Depends(get_current_user)
):
    res = await service.player_ready(match_id, user.id)
    return JSONResponse(content={'result': res})
