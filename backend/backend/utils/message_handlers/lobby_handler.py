from backend.schemas.common_schema import ChannelTypes
from backend.utils.message_handlers.registry import register_channel_handler


@register_channel_handler(ChannelTypes.USER)
async def handle_lobby_subscriptions(message_data: dict, pubsub):
    action = message_data.get('action')
    id = message_data.get('id')
    if action == LobbyAction.ACCEPT_MATCH:
        channel = LobbyKeys.acceptance_channel(id)
        await pubsub.subscribe(channel)