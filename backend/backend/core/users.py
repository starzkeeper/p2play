from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from backend.core.dependencies import user_service
from backend.db.models import User
from backend.services.user_service import UserService
from backend.utils.auth_dependencies import get_current_user

router_users = APIRouter()


@router_users.post("/add_friend")
async def add_friend(
        friend_id: int,
        service: Annotated[UserService, Depends(user_service)],
        user: User = Depends(get_current_user)
):
    res = await service.send_friend_request(friend_id, user.id)
    return JSONResponse(content={'result': res})


@router_users.get("/friend_requests")
async def get_all_friend_requests(
        service: Annotated[UserService, Depends(user_service)],
        user: User = Depends(get_current_user)
):
    res = await service.all_friend_requests(user.id)
    return JSONResponse(content={'result': res})


@router_users.post("/accept_friend_request")
async def accept_friend_request(
        friend_id: int,
        service: Annotated[UserService, Depends(user_service)],
        user: User = Depends(get_current_user)
):
    res = await service.accept_friend_request(friend_id, user.id)
    return JSONResponse(content={'result': res})


@router_users.get("/friends")
async def get_all_friends(
        service: Annotated[UserService, Depends(user_service)],
        user: User = Depends(get_current_user)
):
    res = await service.all_friends(user.id)
    return JSONResponse(content={'result': res})
