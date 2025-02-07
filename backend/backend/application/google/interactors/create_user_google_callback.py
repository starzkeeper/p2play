from dataclasses import dataclass

from backend.adapters.auth.token import JwtTokenProcessor
from backend.application.auth.gateway import RefreshSaver
from backend.application.auth.interactors.authenticate_user import TokenOutputDTO
from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.common.password import get_password_hash, generate_random_password
from backend.application.users.gateway import UserReader, UserSaver
from backend.domain.user.models import UserId, User
from backend.domain.user.value_objects import EmailField


@dataclass
class UserGoogleInfoDTO:
    email: EmailField


class CreateUserGoogleCallback(Interactor[UserGoogleInfoDTO, TokenOutputDTO]):
    def __init__(
            self,
            id_provider: IdProvider,
            user_reader: UserReader,
            user_saver: UserSaver,
            refresh_saver: RefreshSaver,
            token_processor: JwtTokenProcessor
    ):
        self.id_provider = id_provider
        self.user_reader = user_reader
        self.user_saver = user_saver
        self.refresh_saver = refresh_saver
        self.token_processor = token_processor

    async def __call__(self, data: UserGoogleInfoDTO) -> UserId:
        user: User = await self.user_reader.find_one_or_none(data.email)
        if not user:
            user_data = User(email=data.email, password=generate_random_password())
            user_data.password = get_password_hash(user_data.password)
            user_data.is_verified = True
            user = await self.user_saver.create_user(user_data)
        if not user.is_verified:
            user.is_verified = True
            await self.user_saver.update(user)

        refresh_token = self.id_provider.refresh_token
        if refresh_token:
            await self.refresh_saver.delete_refresh_token(refresh_token)
        access_token = self.token_processor.create_access_token(user.id)
        refresh_token = self.token_processor.create_refresh_token()
        await self.refresh_saver.save_refresh_token(user.id, refresh_token)
        return TokenOutputDTO(access_token=access_token, refresh_token=refresh_token)

