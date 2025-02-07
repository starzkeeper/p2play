from dataclasses import dataclass

from backend.application.common.interactor import Interactor
from backend.application.steam.gateway import SteamInterface


@dataclass
class SteamAuthUrlDTO:
    steam_auth_url: str


class CreateSteamAuthUrl(Interactor[None, SteamAuthUrlDTO]):
    def __init__(
            self,
            steam_gateway: SteamInterface,
    ):
        self.steam_gateway = steam_gateway

    async def __call__(self, data: None = None) -> SteamAuthUrlDTO:
        url: str = self.steam_gateway.create_url()
        return SteamAuthUrlDTO(steam_auth_url=url)
