from starlette.requests import Request
from starlette.websockets import WebSocket

from backend.repositories.friend_repository import FriendRepository
from backend.repositories.lobby_repository import LobbyRepository
from backend.repositories.match_repository import MatchRepository
from backend.repositories.user_repository import UserRepository
from backend.repositories.websocket_repository import WebSocketRepository
from backend.services.auth_service import AuthService
from backend.services.lobby_service import LobbyService
from backend.services.match_service import MatchService
from backend.services.user_service import UserService
from backend.services.websocket_service import WebSocketService


def user_service() -> UserService:
    return UserService(UserRepository, FriendRepository)


def auth_service() -> AuthService:
    return AuthService(UserRepository)


def lobby_service(request: Request = None) -> LobbyService:
    return LobbyService(LobbyRepository(request.app.state.redis_client))


def websocket_service(websocket: WebSocket = None) -> WebSocketService:
    return WebSocketService(WebSocketRepository(websocket.app.state.redis_client))


def match_service(request: Request) -> MatchService:
    return MatchService(MatchRepository(request.app.state.redis_client))
