from dataclasses import dataclass
from http.client import HTTPException

from backend.adapters.auth.token import JwtTokenProcessor
from backend.application.auth.gateway import RefreshSaver
from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.common.password import verify_password
from backend.application.errors.user import AuthenticationFailed, UserAlreadyLogged
from backend.application.users.gateway import UserReader, UserSaver
from backend.domain.user.models import UserId
from backend.domain.user.value_objects import EmailField


@dataclass
class UserAuthDTO:
    email: EmailField
    password: str


@dataclass
class TokenOutputDTO:
    access_token: str
    refresh_token: str


class Authenticate(Interactor[UserAuthDTO, TokenOutputDTO]):
    def __init__(
            self,
            id_provider: IdProvider,
            user_reader: UserReader,
            refresh_saver: RefreshSaver,
            token_processor: JwtTokenProcessor
    ):
        self.id_provider = id_provider
        self.user_reader = user_reader
        self.refresh_saver = refresh_saver
        self.token_processor = token_processor

    async def __call__(self, data: UserAuthDTO) -> TokenOutputDTO:
        user = await self.user_reader.find_one_or_none(data.email)
        if not user or verify_password(plain_password=data.password,
                                       hashed_password=user.password) is False:
            raise AuthenticationFailed

        refresh_token = self.id_provider.refresh_token
        if refresh_token:
            await self.refresh_saver.delete_refresh_token(refresh_token)
        access_token = self.token_processor.create_access_token(user.id)
        refresh_token = self.token_processor.create_refresh_token()

        await self.refresh_saver.save_refresh_token(user.id, refresh_token)

        return TokenOutputDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )
