import uuid
from datetime import datetime, UTC, timedelta

from fastapi import Depends, Request, WebSocket, HTTPException
from jose import jwt, JWTError
from starlette import status
from starlette.requests import HTTPConnection

from backend.adapters.persistence.settings import jwt_settings
from backend.application.common.id_provider import IdProvider
from backend.application.users.gateway import UserReader
from backend.domain.access.exceptions import AuthenticationError
from backend.domain.user.models import UserId, User


class JwtTokenProcessor:
    def __init__(
            self
    ):
        pass

    def create_access_token(self, user_id: UserId) -> str:
        to_encode = {"sub": str(user_id)}
        expire = datetime.now(UTC) + timedelta(seconds=jwt_settings.ACCESS_TOKEN_EXPIRES)
        to_encode['exp'] = expire
        to_encode['token_type'] = 'access'
        encode_jwt = jwt.encode(to_encode, key=jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)
        return encode_jwt

    def create_refresh_token(self) -> str:
        token = str(uuid.uuid4())
        return token

    async def validate_access_token(self, token) -> UserId:
        try:
            payload = jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=[jwt_settings.ALGORITHM])
        except JWTError:
            raise AuthenticationError

        token_type = payload.get('token_type')
        if token_type != 'access':
            raise AuthenticationError

        try:
            return UserId(uuid.UUID(payload["sub"]))
        except ValueError:
            raise AuthenticationError


class TokenIdProvider(IdProvider):

    def __init__(
            self,
            token_processor: JwtTokenProcessor,
            user_reader: UserReader,
            connection: HTTPConnection,
    ):
        self.connection = connection
        self.token_processor = token_processor
        self.user_reader = user_reader

    def _extract_token(self, token_type: str) -> str | None:
        token = self.connection.cookies.get(f"user_{token_type}_token")
        return token

    @property
    def access_token(self) -> str | None:
        return self._extract_token('access')

    @property
    def refresh_token(self) -> str | None:
        return self._extract_token('refresh')

    async def get_current_user_id_access_token(self) -> UserId:
        access_token = self.access_token
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not found"
            )
        return await self.token_processor.validate_access_token(self.access_token)

    async def get_current_user(self) -> User:
        user_id: UserId = await self.get_current_user_id_access_token()
        user: User = await self.user_reader.find_one_or_none_by_id(user_id)
        if not user:
            raise AuthenticationError
        return user
