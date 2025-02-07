from redis.asyncio.client import PubSub

from backend.adapters.messages.message import ChannelTypes
from backend.adapters.pubsub.message_handlers.registry import register_channel_handler


@register_channel_handler(ChannelTypes.LOBBY)
async def handle_lobby_subscriptions(message_data: dict, pubsub: PubSub):
    action = message_data.get('action')
    match_id = message_data.get('match_id')
