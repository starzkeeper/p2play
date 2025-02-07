from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, Request

from backend.adapters.auth.google import oauth
from backend.adapters.persistence.settings import jwt_settings
from backend.application.auth.interactors.authenticate_user import Authenticate, UserAuthDTO, TokenOutputDTO
from backend.application.auth.interactors.logout import Logout
from backend.application.auth.interactors.refresh_tokens import RefreshTokens
from backend.application.auth.interactors.register_user import Register, RegisterUserDTO
from backend.application.google.interactors.create_user_google_callback import CreateUserGoogleCallback, \
    UserGoogleInfoDTO
from backend.application.steam.interactors.create_steam_auth_url import CreateSteamAuthUrl
from backend.application.steam.interactors.validate_steam_auth import SteamCallbackInputDTO, ValidateSteamAuth
from backend.domain.user.value_objects import EmailField

router_auth = APIRouter(route_class=DishkaRoute)


@router_auth.post('/register')
async def register_user(
        user_data: RegisterUserDTO,
        service: FromDishka[Register]
):
    res = await service(user_data)
    return {'result': res}


@router_auth.post('/login')
async def login_user(
        response: Response,
        service: FromDishka[Authenticate],
        user_data: UserAuthDTO
):
    tokens: TokenOutputDTO = await service(user_data)
    response.set_cookie(key="user_access_token", value=tokens.access_token, httponly=True, secure=True,
                        max_age=jwt_settings.ACCESS_TOKEN_EXPIRES)
    response.set_cookie(key="user_refresh_token", value=tokens.refresh_token, httponly=True, secure=True,
                        max_age=jwt_settings.REFRESH_TOKEN_EXPIRES, path='/auth')
    return {'result': 'User authenticated'}


@router_auth.post("/logout")
async def logout_user(
        service: FromDishka[Logout],
        response: Response,
):
    await service()
    response.delete_cookie(key="user_access_token")
    response.delete_cookie(key="user_refresh_token")
    return {'message': 'The user successfully logged out of the system'}


@router_auth.get('/google/authorize')
async def google_auth_link(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router_auth.get('/google/callback')
async def google_callback(response: Response, request: Request, service: FromDishka[CreateUserGoogleCallback]):
    token = await oauth.google.authorize_access_token(request)
    user_info = token['userinfo']
    email = EmailField(user_info.get('email'))
    tokens: TokenOutputDTO = await service(UserGoogleInfoDTO(email=email))
    response.set_cookie(key="user_access_token", value=tokens.access_token, httponly=True, secure=True,
                        max_age=jwt_settings.ACCESS_TOKEN_EXPIRES)
    response.set_cookie(key="user_refresh_token", value=tokens.refresh_token, httponly=True, secure=True,
                        max_age=jwt_settings.REFRESH_TOKEN_EXPIRES, path='/auth')
    return {'result': 'Google auth success'}


@router_auth.post('/refresh')
async def refresh_access_token(
        service: FromDishka[RefreshTokens],
        response: Response,
):
    tokens: TokenOutputDTO = await service()
    response.set_cookie(key="user_access_token", value=tokens.access_token, httponly=True, secure=True)
    response.set_cookie(key="user_refresh_token", value=tokens.refresh_token, httponly=True, secure=True, path='/auth')
    return {'result': 'Tokens refreshed'}


@router_auth.get('/steam/authorize')
async def steam_auth_link(
        service: FromDishka[CreateSteamAuthUrl],
):
    res = await service()
    return {"result": res}


@router_auth.get('/steam/callback')
async def steam_callback(
        request: Request,
        service: FromDishka[ValidateSteamAuth],
):
    callback_data = dict(request.query_params)
    input_dto = SteamCallbackInputDTO(callback_data=callback_data)
    res = await service(input_dto)
    return {"result": res}
