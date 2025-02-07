from backend.domain.lobby.exceptions import UserNotInLobbyException, UserInMatch, UserAlreadyInLobby, LobbyIsFull, \
    UserIsNotOwner, LobbyAlreadyInMatch
from backend.domain.lobby.models import Lobby, LobbyStatus
from backend.domain.user.models import UserId


def check_user_in_players(user_id: UserId, players: list):
    if user_id not in players:
        raise UserNotInLobbyException


def remove_player_from_lobby(lobby: Lobby, user_id: UserId) -> Lobby:
    if lobby.lobby_status not in (LobbyStatus.SEARCHING, LobbyStatus.WAITING):
        raise UserInMatch

    if lobby.lobby_status == LobbyStatus.SEARCHING:
        lobby.lobby_status = LobbyStatus.WAITING

    lobby.players.remove(user_id)

    if lobby.owner_id == user_id:
        lobby.owner_id = lobby.players[0]

    return lobby


def can_add_player_to_lobby(lobby: Lobby, user_id: UserId) -> Lobby:
    if lobby.lobby_status == LobbyStatus.SEARCHING:
        raise LobbyAlreadyInMatch

    if user_id in lobby.players:
        raise UserAlreadyInLobby

    if len(lobby.players) >= 5:
        raise LobbyIsFull


def check_user_is_owner(owner_id: UserId, user_id: UserId) -> bool:
    if owner_id != user_id:
        raise UserIsNotOwner
    return True
