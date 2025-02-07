from backend.domain.friendship.exceptions import FriendRequestException


def ensure_can_send_friend_request(friend_id: int, user_id: int):
    if friend_id != user_id:
        return
    raise FriendRequestException
