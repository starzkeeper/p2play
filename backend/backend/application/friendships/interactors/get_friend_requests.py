from dataclasses import dataclass

from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.friendships.gateway import FriendshipReader
from backend.domain.user.models import UserId


@dataclass
class FriendshipReceivedRequestsDTO:
    received_request_ids: list[UserId]


class GetFriendReceivedRequests(Interactor[None, FriendshipReceivedRequestsDTO]):
    def __init__(
            self,
            friendship_reader: FriendshipReader,
            id_provider: IdProvider
    ):
        self.friendship_reader = friendship_reader
        self.id_provider = id_provider

    async def __call__(self, data: None = None) -> FriendshipReceivedRequestsDTO:
        user_id = await self.id_provider.get_current_user_id_access_token()
        received_requests_ids: list = await self.friendship_reader.friend_received_requests(user_id)

        return FriendshipReceivedRequestsDTO(received_requests_ids)
