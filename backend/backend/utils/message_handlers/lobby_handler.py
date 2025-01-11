from redis.asyncio.client import PubSub

from backend.schemas.common_schema import ChannelTypes
from backend.schemas.lobby_schema import LobbyAction, AcceptanceAction
from backend.utils.message_handlers.registry import register_channel_handler
from backend.utils.redis_keys import MatchKeys


@register_channel_handler(ChannelTypes.LOBBY)
async def handle_lobby_subscriptions(message_data: dict, pubsub: PubSub):
    action = message_data.get('action')
    match_id = message_data.get('match_id')

