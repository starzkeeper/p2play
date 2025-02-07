from backend.adapters.auth.token import JwtTokenProcessor
from backend.application.auth.gateway import RefreshReader, RefreshSaver
from backend.application.auth.interactors.authenticate_user import TokenOutputDTO
from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.users.gateway import UserSaver


class RefreshTokens(Interactor[None, TokenOutputDTO]):
    def __init__(
            self,
            id_provider: IdProvider,
            refresh_reader: RefreshReader,
            refresh_saver: RefreshSaver,
            token_processor: JwtTokenProcessor,
    ):
        self.id_provider = id_provider
        self.refresh_reader = refresh_reader
        self.refresh_saver = refresh_saver
        self.token_processor = token_processor

    async def __call__(self, data: None = None) -> TokenOutputDTO:
        refresh_token = self.id_provider.refresh_token
        user_id = await self.refresh_reader.read_refresh_token(refresh_token)

        await self.refresh_saver.delete_refresh_token(refresh_token)

        access_token = self.token_processor.create_access_token(user_id)
        new_refresh_token = self.token_processor.create_refresh_token()

        return TokenOutputDTO(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )
