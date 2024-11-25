from starlette.requests import Request
from starlette.websockets import WebSocket

from backend.repositories.friend_repository import FriendRepository
from backend.repositories.lobby_repository import LobbyRepository
from backend.repositories.user_repository import UserRepository
from backend.services.auth_service import AuthService
from backend.services.lobby_service import LobbyService
from backend.services.user_service import UserService


def user_service():
    return UserService(UserRepository, FriendRepository)


def auth_service():
    return AuthService(UserRepository)


def lobby_service(request: Request = None, websocket: WebSocket = None) -> LobbyService:
    if request is None:
        return LobbyService(LobbyRepository(websocket.app.state.redis_client))
    else:
        return LobbyService(LobbyRepository(request.app.state.redis_client))
