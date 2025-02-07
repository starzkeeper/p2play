from redis.asyncio.client import PubSub

from backend.adapters.messages.message import ChannelTypes
from backend.adapters.persistence.redis_keys import MatchKeys
from backend.domain.lobby.models import AcceptanceAction
from backend.adapters.pubsub.message_handlers.registry import register_channel_handler


@register_channel_handler(ChannelTypes.ACCEPTANCE)
async def handle_lobby_subscriptions(message_data: dict, pubsub: PubSub):
    action = message_data.get('action')
    match_id = message_data.get('match_id')

    if action == AcceptanceAction.CANCEL_MATCH:
        await pubsub.unsubscribe(MatchKeys.match_channel(match_id))
