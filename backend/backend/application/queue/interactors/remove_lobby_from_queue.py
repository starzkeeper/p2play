from dataclasses import dataclass

from backend.application.common.interactor import Interactor
from backend.application.queue.gateway import QueueSaver
from backend.domain.lobby.models import LobbyId


@dataclass
class RemoveFromQueueInputDTO:
    lobby_id: LobbyId


class RemoveFromQueue(Interactor[RemoveFromQueueInputDTO, None]):
    def __init__(
            self,
            queue_saver: QueueSaver
    ):
        self.queue_saver = queue_saver

    async def __call__(self, data: RemoveFromQueueInputDTO) -> None:
        await self.queue_saver.remove_from_queue(data.lobby_id)
