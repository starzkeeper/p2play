from dataclasses import dataclass

from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.errors.lobby import LobbyDoesNotExist
from backend.application.lobby.gateway import LobbyReader
from backend.domain.lobby.models import Lobby


@dataclass
class LobbyDTO:
    pass


class GetUserLobby(Interactor[None, Lobby | None]):
    def __init__(
            self,
            lobby_reader: LobbyReader,
            id_provider: IdProvider,
    ):
        self.lobby_reader = lobby_reader
        self.id_provider = id_provider

    async def __call__(self, data: None = None) -> Lobby | None:
        user_id = await self.id_provider.get_current_user_id_access_token()
        lobby_id = await self.lobby_reader.get_user_lobby_id(user_id)
        if not lobby_id:
            return None
        lobby, _ = await self.lobby_reader.get_lobby(lobby_id)
        return lobby

