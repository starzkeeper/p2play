from dataclasses import dataclass

from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.friendships.gateway import FriendshipSaver
from backend.domain.friendship.models import FriendshipId
from backend.domain.user.models import UserId
from backend.domain.friendship.services import ensure_can_send_friend_request


@dataclass(frozen=True)
class FriendshipRequestDTO:
    friend_id: UserId


class AcceptFriendRequest(Interactor[FriendshipRequestDTO, None]):
    def __init__(
            self,
            friendship_saver: FriendshipSaver,
            id_provider: IdProvider
    ):
        self.friendship_saver = friendship_saver
        self.id_provider = id_provider

    async def __call__(self, data: FriendshipRequestDTO) -> None:
        user_id = await self.id_provider.get_current_user_id_access_token()
        ensure_can_send_friend_request(data.friend_id, user_id)
        await self.friendship_saver.accept_friend_request(data.friend_id, user_id)
