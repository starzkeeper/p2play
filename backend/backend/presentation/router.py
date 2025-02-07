from backend.presentation.routers import router_auth, router_lobby, router_users  # router_match, router_websocket
from backend.presentation.routers.websocket import router_websocket

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
    # {
    #     "router": router_match,
    #     "prefix": '/match',
    #     "tags": ["Match"]
    # },
    {
        "router": router_websocket,
        "prefix": '/websockets',
        "tags": ["Websockets"]
    }
]
