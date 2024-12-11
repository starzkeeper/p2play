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


class MatchKeys:
    @staticmethod
    def match_channel(match_id: str) -> str:
        return f"match_channel:{match_id}"

    @staticmethod
    def match(match_id: str) -> str:
        return f"match_{match_id}"
