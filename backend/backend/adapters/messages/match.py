from backend.adapters.messages.message import Message
from backend.domain.match.models import MatchId


class MatchMessage(Message):
    from_match_id: MatchId
