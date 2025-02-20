from backend.adapters.messages.message import Message, ChannelTypes
from backend.domain.match.models import MatchId


class MatchMessage(Message):
    from_match_id: MatchId
    type: ChannelTypes = ChannelTypes.MATCH
