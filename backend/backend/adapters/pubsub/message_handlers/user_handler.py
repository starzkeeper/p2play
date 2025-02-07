import logging

from backend.adapters.messages.message import ChannelTypes
from backend.adapters.persistence.redis_keys import LobbyKeys
from backend.domain.lobby.models import UserAction
from backend.adapters.pubsub.message_handlers.registry import register_channel_handler

logger = logging.getLogger('p2play')


@register_channel_handler(ChannelTypes.USER)
async def handle_user_subscriptions(message_data: dict, pubsub):
    action = message_data.get('action')
    lobby_id = message_data.get('lobby_id')

    if action == UserAction.JOIN_LOBBY:
        channel = LobbyKeys.lobby_channel(lobby_id)
        await pubsub.subscribe(channel)
        logger.debug(f'Channel subscribe: {channel}')
    elif action == UserAction.LEAVE_LOBBY:
        channel = LobbyKeys.lobby_channel(lobby_id)
        await pubsub.unsubscribe(channel)
        logger.debug(f'Channel unsubscribe: {channel}')
    return
