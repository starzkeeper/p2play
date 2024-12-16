from typing import Callable, Dict
from backend.schemas.common_schema import ChannelTypes

CHANNEL_HANDLERS: Dict[ChannelTypes, Callable] = {}


def register_channel_handler(channel_type: ChannelTypes):
    """
    Декоратор для регистрации обработчика канала.
    Использование:

    @register_channel_handler(ChannelTypes.USER)
    async def handle_user_subscriptions(message_data, pubsub):
        ...
    """

    def decorator(func: Callable):
        CHANNEL_HANDLERS[channel_type] = func
        return func

    return decorator
