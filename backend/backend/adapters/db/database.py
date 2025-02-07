import logging
import os
from asyncio import current_task
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, async_scoped_session, AsyncSession

from backend.adapters.persistence.settings import redis_settings

logger = logging.getLogger("p2play")

# POSTGRESQL

DATABASE_URL = os.getenv('POSTGRES_URL')

engine = create_async_engine(DATABASE_URL)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def scoped_session():
    scoped_factory = async_scoped_session(
        async_session_factory,
        scopefunc=current_task,
    )
    try:
        async with scoped_factory() as s:
            yield s
    finally:
        await scoped_factory.remove()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


# REDIS
async def redis_pool():
    redis_client = Redis(
        host=redis_settings.REDIS_HOST,
        port=redis_settings.REDIS_PORT,
        decode_responses=True,
    )
    try:
        await redis_client.ping()
        logger.info('Redis is connected')
    except Exception as e:
        logger.info(f'Redis is not connected: {e}')
    return redis_client

