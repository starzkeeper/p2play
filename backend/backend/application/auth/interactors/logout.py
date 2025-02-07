from backend.application.auth.gateway import RefreshSaver
from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor


class Logout(Interactor[None, None]):
    def __init__(
            self,
            refresh_saver: RefreshSaver,
            id_provider: IdProvider,
    ):
        self.refresh_saver = refresh_saver
        self.id_provider = id_provider

    async def __call__(self, data: None = None) -> None:
        refresh_token = self.id_provider.refresh_token
        await self.refresh_saver.delete_refresh_token(refresh_token)


