from backend.exceptions.exceptions import InvalidOperationError, EntityDoesNotExistError
from backend.repositories.friend_repository import FriendRepository
from backend.repositories.user_repository import UserRepository
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus


class UserService:
    def __init__(self, user_repository: UserRepository, friend_repository: FriendRepository):
        self.user_repository = user_repository
        self.friend_repository = friend_repository

    async def send_friend_request(self, friend_id: int, user_id: int):
        if friend_id == user_id:
            raise InvalidOperationError
        friend = await self.user_repository.find_one_or_none_by_id(friend_id)
        if not friend:
            raise EntityDoesNotExistError('User')

        await self.friend_repository.create_friend_request(friend_id, user_id)
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message='Friend request created successfully.'
        )

    async def all_friend_requests(self, user_id: int):
        # TODO: info about users
        sent_requests_ids: list = await self.friend_repository.friend_sent_requests(user_id)
        received_requests_ids: list = await self.friend_repository.friend_received_requests(user_id)

        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message={
                'sent_request_ids': sent_requests_ids,
                'received_request_ids': received_requests_ids
            }
        )

    async def accept_friend_request(self, friend_id: int, user_id: int):
        if friend_id == user_id:
            raise InvalidOperationError
        await self.friend_repository.accept_friend_request(friend_id, user_id)
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message='Friend request accepted successfully.'
        )

    async def all_friends(self, user_id: int):
        friends: list = await self.friend_repository.all_friends(user_id)
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=friends
        )



