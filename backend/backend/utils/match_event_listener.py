import asyncio
import logging

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

logger = logging.getLogger('p2play')


async def expired_listener(redis_client: Redis):
    """
    Одна корутина, подписана на __keyevent@0__:expired.
    Если истёк ban_lock:{match_id}, значит капитан не успел забанить за 30 сек.
    => Авто-баним случайную карту.
    """
    pubsub: PubSub = redis_client.pubsub()
    await pubsub.psubscribe("__keyevent@0__:expired")
    logger.info("[expired_listener] Subscribed to __keyevent@0__:expired")

    try:
        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                expired_key_bytes = message["data"]
                if expired_key_bytes and isinstance(expired_key_bytes, bytes):
                    key_str = expired_key_bytes.decode("utf-8")

                    if key_str.startswith("ban_lock:"):
                        match_id = key_str.split(":")[1]
                        logger.info(f"[expired_listener] ban_lock expired => match_id={match_id}")

                        await auto_ban(match_id)

    except asyncio.CancelledError:
        logger.warning("[expired_listener] Cancelled.")
    finally:
        await pubsub.close()
        logger.info("[expired_listener] pubsub closed.")
