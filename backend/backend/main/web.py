from contextlib import asynccontextmanager
import logging
from logging.config import dictConfig

from dishka.integrations.fastapi import setup_dishka
from redis.asyncio import Redis
from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.adapters.db.models.map import map_tables
from backend.adapters.persistence.settings import LogConfig, redis_settings, jwt_settings
from backend.main.di import setup_di
from backend.presentation.router import routers

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("p2play")

REDIS_HOST = redis_settings.REDIS_HOST
REDIS_PORT = redis_settings.REDIS_PORT


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will run before app starts handling requests
    yield
    # This will run after the app finishes handling requests
    await app.state.dishka_container.close()


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
app.add_middleware(SessionMiddleware, secret_key=jwt_settings.SECRET_KEY)


@app.get("/v1/health", tags=['Health check'])
async def health():
    return "I'm alive!"


for route in routers:
    app.include_router(route["router"], prefix=route["prefix"], tags=route["tags"])

map_tables()
setup_dishka(container=setup_di(), app=app)

# @app.exception_handler(BaseCustomException)
# async def base_custom_exception_handler(request: Request, exc: BaseCustomException):
#     logger.debug(exc)
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"message": exc.message}
#     )
