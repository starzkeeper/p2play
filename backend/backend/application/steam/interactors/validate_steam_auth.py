from dataclasses import dataclass

from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.steam.gateway import SteamInterface
from backend.application.users.gateway import UserSaver
from backend.domain.user.models import SteamId


@dataclass
class SteamCallbackInputDTO:
    callback_data: dict


class ValidateSteamAuth(Interactor[SteamCallbackInputDTO, SteamId]):
    def __init__(
            self,
            user_saver: UserSaver,
            id_provider: IdProvider,
            steam_gateway: SteamInterface
    ):
        self.user_saver = user_saver
        self.id_provider = id_provider
        self.steam_gateway = steam_gateway

    async def __call__(self, data: SteamCallbackInputDTO):
        user_id = await self.id_provider.get_current_user_id_access_token()
        steam_id: str = self.steam_gateway.validate_response(data.callback_data)
        steam_id: int = str(steam_id)
        await self.user_saver.insert_steam_id(steam_id=steam_id, user_id=user_id)
        return SteamId(steam_id)
