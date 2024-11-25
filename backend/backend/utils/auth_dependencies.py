from typing import Annotated

from jose import jwt, JWTError

from fastapi import Request, HTTPException, status, Depends
from starlette.websockets import WebSocket

from backend.core.dependencies import auth_service
from backend.core.settings import settings
from backend.services.auth_service import AuthService


def get_token(request: Request = None, websocket: WebSocket = None):
    token = None
    if request:
        token = request.cookies.get('users_access_token')
    elif websocket:
        token = websocket.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token


def get_refresh_token(request: Request):
    token = request.cookies.get('users_refresh_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token not found')
    return token


async def get_current_user(service: Annotated[AuthService, Depends(auth_service)], token: str = Depends(get_token)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token is invalid!')

    user_id = payload.get('sub')
    token_type = payload.get('token_type')
    if token_type != 'access':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token is invalid!')

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User ID not found')

    user = await service.user_repository.find_one_or_none_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    return user
