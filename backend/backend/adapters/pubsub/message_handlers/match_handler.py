from redis.asyncio.client import PubSub

from backend.adapters.messages.message import ChannelTypes
from backend.adapters.pubsub.message_handlers.registry import register_channel_handler
from backend.domain.match.models import MatchAction


@register_channel_handler(ChannelTypes.ACCEPTANCE)
async def handle_lobby_subscriptions(message_data: dict, pubsub: PubSub):
    action = message_data.get('action')

    # if action == MatchAction.MATCH_PREPARATION_STARTED:
