from backend.core.auth import router_auth
from backend.core.lobby import router_lobby
from backend.core.match import router_match
from backend.core.users import router_users
from backend.core.websocket import router_websocket

routers = [
    {
        "router": router_auth,
        "prefix": '/auth',
        "tags": ["Auth"]
    },
    {
        "router": router_users,
        "prefix": '/users',
        "tags": ["Users"]
    },
    {
        "router": router_lobby,
        "prefix": '/lobby',
        "tags": ["Lobby"]
    },
    {
        "router": router_match,
        "prefix": '/match',
        "tags": ["Match"]
    },
    {
        "router": router_websocket,
        "prefix": '/websockets',
        "tags": ["Websockets"]
    }
]
