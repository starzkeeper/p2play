from dataclasses import dataclass

from backend.application.common.interactor import Interactor
from backend.application.queue.gateway import QueueSaver
from backend.domain.lobby.models import LobbyId


@dataclass
class QueueInputDTO:
    lobby_id: LobbyId


class AddLobbyToQueue(Interactor[QueueInputDTO, None]):
    def __init__(
            self,
            queue_saver: QueueSaver,
    ):
        self.queue_saver = queue_saver

    async def __call__(self, data: QueueInputDTO) -> None:
        await self.queue_saver.add_to_queue(data.lobby_id)
