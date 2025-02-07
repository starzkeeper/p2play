from backend.domain.match.exceptions import UserNotInMatch
from backend.domain.match.models import Match
from backend.domain.user.models import UserId


def check_user_in_match(match: Match, user_id: UserId):
    if (user_id not in match.team_1) or (user_id not in match.team_2):
        raise UserNotInMatch
