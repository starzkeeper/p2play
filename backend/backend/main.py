from contextlib import asynccontextmanager
import logging
from logging.config import dictConfig

from redis.asyncio import Redis
from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from backend.core.router import routers
from backend.core.settings import settings, LogConfig

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("p2play")

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT


async def redis_pool():
    redis_client = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )
    try:
        await redis_client.ping()
        logger.info('Redis is connected')
    except Exception as e:
        logger.info(f'Redis is not connected: {e}')
    return redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will run before app starts handling requests
    app.state.redis_client = await redis_pool()
    yield
    # This will run after the app finishes handling requests
    await app.state.redis_client.close()


app = FastAPI(lifespan=lifespan)

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


@app.get("/v1/health", tags=['Health check'])
async def health():
    return "I'm alive!"


for route in routers:
    app.include_router(route["router"], prefix=route["prefix"], tags=route["tags"])
