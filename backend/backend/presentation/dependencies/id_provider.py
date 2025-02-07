from typing import Annotated


from fastapi import Cookie, Request
from starlette.websockets import WebSocket

from backend.adapters.auth.token import JwtTokenProcessor, TokenIdProvider
from backend.application.common.id_provider import IdProvider


