from backend.core.auth import router_auth
from backend.core.lobby import router_lobby
from backend.core.users import router_users

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
    }
]
