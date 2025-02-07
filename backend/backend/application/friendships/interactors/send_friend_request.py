from backend.application.common.id_provider import IdProvider
from backend.application.common.interactor import Interactor
from backend.application.errors.exceptions import EntityDoesNotExistError
from backend.application.friendships.gateway import FriendshipSaver
from backend.application.friendships.interactors.accept_friend_request import FriendshipRequestDTO
from backend.application.users.gateway import UserReader
from backend.domain.friendship.services import ensure_can_send_friend_request


class SendFriendRequest(Interactor[FriendshipRequestDTO, None]):
    def __init__(
            self,
            friendship_saver: FriendshipSaver,
            user_reader: UserReader,
            id_provider: IdProvider
    ):
        self.friendship_saver = friendship_saver
        self.user_reader = user_reader
        self.id_provider = id_provider

    async def __call__(self, data: FriendshipRequestDTO) -> None:
        user_id = await self.id_provider.get_current_user_id_access_token()
        ensure_can_send_friend_request(data.friend_id, user_id)
        friend = await self.user_reader.find_one_or_none_by_id(data.friend_id)
        if not friend:
            raise EntityDoesNotExistError

        await self.friendship_saver.create_friend_request(data.friend_id, user_id)
