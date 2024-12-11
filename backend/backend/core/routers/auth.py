from typing import Annotated

from fastapi import APIRouter, Depends, Response, Request
from starlette.responses import JSONResponse

from backend.core.dependencies import auth_service
from backend.core.settings import settings
from backend.db.models import User
from backend.schemas.response_schema import DefaultApiResponse
from backend.schemas.user_schema import UserCreate, UserAuth
from backend.services.auth_service import AuthService
from backend.utils.auth_dependencies import get_current_user, get_refresh_token
from backend.utils.google import oauth

router_auth = APIRouter()


@router_auth.post('/register')
async def register_user(
        user_data: UserCreate,
        service: Annotated[AuthService, Depends(auth_service)]
):
    res = await service.register_user(user_data)
    return JSONResponse(content={'result': res})


@router_auth.post('/login')
async def login_user(
        response: Response,
        service: Annotated[AuthService, Depends(auth_service)],
        user_data: UserAuth
):
    res: DefaultApiResponse = await service.authenticate_user(user_data)
    if res['status'] == 'success':
        access_token = res['message']['access_token']
        refresh_token = res['message']['refresh_token']
        response.set_cookie(key="users_access_token", value=access_token, httponly=True, secure=True,
                            max_age=settings.ACCESS_TOKEN_EXPIRES)
        response.set_cookie(key="users_refresh_token", value=refresh_token, httponly=True, secure=True,
                            max_age=settings.REFRESH_TOKEN_EXPIRES)
    return {'result': res}


@router_auth.post("/logout")
async def logout_user(
        response: Response,
        user_data: User = Depends(get_current_user)
):
    response.delete_cookie(key="users_access_token")
    response.delete_cookie(key="users_refresh_token")
    return {'message': 'The user successfully logged out of the system'}


@router_auth.get('/google/authorize')
async def google_auth_link(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router_auth.get('/google/callback')
async def google_callback(request: Request, service: Annotated[AuthService, Depends(auth_service)]):
    token = await oauth.google.authorize_access_token(request)
    user = token['userinfo']
    res = await service.google_auth(user)
    return JSONResponse(content={'result': res})


@router_auth.post('/refresh')
async def refresh_access_token(
        service: Annotated[AuthService, Depends(auth_service)],
        response: Response,
        refresh_token: str = Depends(get_refresh_token),
):
    res = await service.validate_refresh_token(refresh_token)
    if res['status'] == 'success':
        access_token = res['message']['access_token']
        refresh_token = res['message']['refresh_token']
        response.set_cookie(key="users_access_token", value=access_token, httponly=True, secure=True,
                            max_age=settings.ACCESS_TOKEN_EXPIRES)
        response.set_cookie(key="users_refresh_token", value=refresh_token, httponly=True, secure=True,
                            max_age=settings.REFRESH_TOKEN_EXPIRES)
    return {'result': res}


@router_auth.get('/steam/authorize')
async def steam_auth_link(
        service: Annotated[AuthService, Depends(auth_service)],
        user_data: User = Depends(get_current_user)
):
    res = await service.get_steam_authorization_url()
    return JSONResponse(content={"result": res})


@router_auth.get('/steam/callback')
async def steam_callback(
        request: Request,
        service: Annotated[AuthService, Depends(auth_service)],
        user: User = Depends(get_current_user)
):
    res = await service.validate_steam_auth(request, user.id)
    return JSONResponse(content={"result": res})
