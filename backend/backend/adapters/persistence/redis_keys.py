from backend.domain.lobby.models import LobbyId


class UserKeys:
    @staticmethod
    def user_channel(user_id: int) -> str:
        return f"user_channel:{user_id}"

    @staticmethod
    def user_lobby_id(user_id: int) -> str:
        return f"user:{user_id}:lobby_id"

    @staticmethod
    def user_match_id(user_id: int) -> str:
        return f"user:{user_id}:match_id"


class LobbyKeys:
    @staticmethod
    def lobby_channel(lobby_id: str) -> str:
        return f"lobby_channel:{lobby_id}"

    @staticmethod
    def lobby(lobby_id: str) -> str:
        return f"lobby_{lobby_id}"

    @staticmethod
    def acceptance(match_id: str) -> str:
        return f"acceptance:{match_id}:players"

    @staticmethod
    def acceptance_meta(match_id: str) -> str:
        return f"acceptance_meta:{match_id}"

    @staticmethod
    def players(lobby_id: LobbyId) -> str:
        return f"players:{lobby_id}"


class MatchKeys:
    @staticmethod
    def match_channel(match_id: str) -> str:
        return f"match_channel:{match_id}"

    @staticmethod
    def match(match_id: str) -> str:
        return f"match_{match_id}"

class RefreshKeys:
    @staticmethod
    def refresh(refresh_token: str) -> str:
        return f"refresh_token:{refresh_token}"


# def resolver_channels(channel_id: str, channel_type: ChannelTypes) -> str:
#     channel_names = {
#         ChannelTypes.LOBBY: LobbyKeys.lobby_channel(channel_id),
#         ChannelTypes.MATCH: MatchKeys.match_channel(channel_id),
#     }
#
#     if channel_type not in channel_names:
#         raise EntityDoesNotExistError(channel_type)
#
#     return channel_names[channel_type]
