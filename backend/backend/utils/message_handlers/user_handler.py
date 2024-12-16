import logging

from backend.schemas.common_schema import ChannelTypes
from backend.utils.message_handlers.registry import register_channel_handler

logger = logging.getLogger('p2play')


@register_channel_handler(ChannelTypes.USER)
async def handle_user_subscriptions(message_data: dict, pubsub):
    action = message_data.get('action')
    id = message_data.get('id')

    if action == ServiceAction.JOIN_LOBBY:
        channel = LobbyKeys.lobby_channel(id)
        await pubsub.subscribe(channel)
        logger.debug(f'Channel subscribe: {channel}')
    elif action == ServiceAction.LEAVE_LOBBY:
        channel = LobbyKeys.lobby_channel(id)
        await pubsub.unsubscribe(channel)
        logger.debug(f'Channel unsubscribe: {channel}')
    return
