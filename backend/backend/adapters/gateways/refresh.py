import uuid

from redis.asyncio import Redis

from backend.adapters.persistence.redis_keys import RefreshKeys
from backend.adapters.persistence.settings import jwt_settings
from backend.application.auth.gateway import RefreshSaver, RefreshReader
from backend.domain.access.exceptions import TokenNotExist
from backend.domain.user.models import UserId


class RefreshGateway(RefreshReader, RefreshSaver):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def save_refresh_token(self, user_id: UserId, refresh_token: str) -> None:
        await self.redis_client.setex(RefreshKeys.refresh(refresh_token), jwt_settings.REFRESH_TOKEN_EXPIRES,
                                      str(user_id))

    async def read_refresh_token(self, refresh_token: str) -> UserId:
        user_id = await self.redis_client.get(RefreshKeys.refresh(refresh_token))
        if user_id is None:
            raise TokenNotExist
        return UserId(uuid.UUID(user_id))

    async def delete_refresh_token(self, refresh_token: str) -> None:
        await self.redis_client.delete(RefreshKeys.refresh(refresh_token))
