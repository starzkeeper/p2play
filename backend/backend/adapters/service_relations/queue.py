from backend.application.lobby.services_interface import QueueServiceInterface
from backend.application.queue.interactors.add_lobby_to_queue import QueueInputDTO, AddLobbyToQueue
from backend.application.queue.interactors.remove_lobby_from_queue import RemoveFromQueueInputDTO, RemoveFromQueue


class QueueServiceGateway(QueueServiceInterface):
    def __init__(
            self,
            add_to_queue: AddLobbyToQueue,
            remove_from_queue: RemoveFromQueue,
    ):
        self.add_to_queue = add_to_queue
        self.remove_from_queue = remove_from_queue

    async def add_to_queue(self, data: QueueInputDTO) -> None:
        await self.add_to_queue(data)

    async def remove_from_queue(self, data: RemoveFromQueueInputDTO) -> None:
        await self.remove_from_queue(data)
