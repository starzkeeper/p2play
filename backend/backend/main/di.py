import logging
from typing import AsyncIterator

from dishka import (
    AnyOf,
    AsyncContainer,
    Provider,
    Scope,
    make_async_container,
    provide, )
from dishka.exceptions import NoContextValueError
from dishka.integrations.fastapi import FastapiProvider
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from redis.asyncio import Redis
from fastapi import WebSocket, Request

from backend.adapters.auth.token import JwtTokenProcessor, TokenIdProvider
from backend.adapters.db.database import redis_pool
from backend.adapters.gateways.friendship import FriendshipGateway
from backend.adapters.gateways.lobby import LobbyGateway, LobbyPubSubGateway
from backend.adapters.gateways.match import MatchGateway
from backend.adapters.gateways.refresh import RefreshGateway
from backend.adapters.pubsub.pubsub import PubSubGateway
from backend.adapters.gateways.queue import QueueGateway
from backend.adapters.gateways.user import UserGateway, UserPubSubGateway

from backend.adapters.steam.steam_processor import SteamProcessor
from backend.application.auth.gateway import RefreshReader, RefreshSaver
from backend.application.auth.interactors.authenticate_user import Authenticate
from backend.application.auth.interactors.logout import Logout
from backend.application.auth.interactors.refresh_tokens import RefreshTokens
from backend.application.auth.interactors.register_user import Register
from backend.application.common.id_provider import IdProvider
from backend.application.friendships.gateway import FriendshipReader, FriendshipSaver
from backend.application.friendships.interactors.accept_friend_request import AcceptFriendRequest
from backend.application.friendships.interactors.get_friend_requests import GetFriendReceivedRequests
from backend.application.friendships.interactors.get_friends import GetAllFriends
from backend.application.friendships.interactors.get_sent_friend_requests import GetSentFriendRequests
from backend.application.friendships.interactors.send_friend_request import SendFriendRequest
from backend.application.google.interactors.create_user_google_callback import CreateUserGoogleCallback
from backend.application.lobby.gateway import LobbyReader, LobbySaver, QueueReader, QueueSaver, LobbyPubSubInterface
from backend.application.lobby.interactors.create_lobby import CreateLobby
from backend.application.lobby.interactors.get_lobby_by_uid import GetUserLobby
from backend.application.lobby.interactors.join_lobby import JoinLobby
from backend.application.lobby.interactors.player_ready import PlayerReady
from backend.application.lobby.interactors.remove_player import RemovePlayer
from backend.application.lobby.interactors.send_lobby_message import SendChatLobbyMessage
from backend.application.lobby.interactors.start_searching import StartSearching
from backend.application.lobby.interactors.stop_searching import StopSearching
from backend.application.match.gateway import MatchSaver, MatchReader
from backend.application.match.interactors.get_maps import GetMaps
from backend.application.match.interactors.get_match_by_id import GetMatchById
from backend.application.steam.gateway import SteamInterface
from backend.application.steam.interactors.create_steam_auth_url import CreateSteamAuthUrl
from backend.application.steam.interactors.validate_steam_auth import ValidateSteamAuth
from backend.application.users.gateway import UserReader, UserSaver, UserPubSubInterface
from backend.application.websocket.gateway import PubSubInterface
from backend.application.websocket.interactors.connect_websocket import ConnectWebsocket
from backend.presentation.websocket_handler import WebSocketHandler

logger = logging.getLogger('p2play')


def gateway_provider() -> Provider:
    provider = Provider()

    provider.provide(
        UserGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[UserReader, UserSaver],
    )
    provider.provide(
        FriendshipGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[FriendshipReader, FriendshipSaver],
    )
    provider.provide(
        LobbyGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[LobbyReader, LobbySaver],
    )
    provider.provide(
        QueueGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[QueueReader, QueueSaver],
    )
    provider.provide(
        MatchGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[MatchSaver, MatchReader]
    )
    provider.provide(
        LobbyPubSubGateway,
        scope=Scope.REQUEST,
        provides=LobbyPubSubInterface
    )
    provider.provide(
        UserPubSubGateway,
        scope=Scope.REQUEST,
        provides=UserPubSubInterface
    )
    provider.provide(
        RefreshGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[RefreshReader, RefreshSaver]
    )

    return provider


def infrastructure_provider() -> Provider:
    provider = Provider()
    provider.provide(JwtTokenProcessor, scope=Scope.REQUEST)
    provider.provide(
        SteamProcessor,
        scope=Scope.REQUEST,
        provides=SteamInterface
    )

    return provider


def interactor_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    # Auth
    provider.provide(Authenticate)
    provider.provide(Register)
    provider.provide(RefreshTokens)
    provider.provide(Logout)

    # Friendship
    provider.provide(AcceptFriendRequest)
    provider.provide(GetFriendReceivedRequests)
    provider.provide(GetAllFriends)
    provider.provide(GetSentFriendRequests)
    provider.provide(SendFriendRequest)

    # Google
    provider.provide(CreateUserGoogleCallback)

    # Lobby
    provider.provide(CreateLobby)
    provider.provide(GetUserLobby)
    provider.provide(JoinLobby)
    provider.provide(PlayerReady)
    provider.provide(RemovePlayer)
    provider.provide(StartSearching)
    provider.provide(SendChatLobbyMessage)
    provider.provide(StopSearching)

    # Match
    provider.provide(GetMatchById)
    provider.provide(GetMaps)

    # Steam
    provider.provide(CreateSteamAuthUrl)
    provider.provide(ValidateSteamAuth)

    # Websocket
    provider.provide(ConnectWebsocket)

    return provider


# def config_provider() -> Provider:
#     provider = Provider(scope=Scope.APP)
#     provider.provide(Settings)
#     provider.provide(JwtSettings)
#     provider.provide(RedisSettings)
#     provider.provide(GoogleSettings)
#
#     return provider


class JwtProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_id_provider(
            self,
            token_processor: JwtTokenProcessor,
            user_reader: UserReader,
            container: AsyncContainer
    ) -> IdProvider:
        try:
            x = await container.get(Request)
        except NoContextValueError:
            x = await container.get(WebSocket)
        return TokenIdProvider(
            token_processor=token_processor,
            user_reader=user_reader,
            connection=x
        )


class MongoProvider(Provider):
    @provide(scope=Scope.APP)
    def get_mongo_client(self) -> AsyncMongoClient:
        return AsyncMongoClient("mongodb", 27017, uuidRepresentation='standard')

    @provide(scope=Scope.APP)
    def get_mongo_db(self, client: AsyncMongoClient) -> AsyncDatabase:
        return client["p2play"]


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis(self) -> AsyncIterator[Redis]:
        redis_client = await redis_pool()
        yield redis_client
        await redis_client.close()

    @provide(scope=Scope.SESSION)
    async def get_pubsub(self, redis_client: Redis, websocket: WebSocket) -> PubSubInterface:
        pubsub_client = redis_client.pubsub()
        return PubSubGateway(
            websocket=websocket,
            pubsub=pubsub_client
        )


class WebSocketProvider(Provider):
    @provide(scope=Scope.SESSION)
    async def get_websocket_handler(self, websocket: WebSocket, pubsub_gateway: PubSubInterface) -> WebSocketHandler:
        return WebSocketHandler(websocket, pubsub_gateway)


def setup_providers() -> list[Provider]:
    providers = [
        gateway_provider(),
        interactor_provider(),
        infrastructure_provider()
    ]

    return providers


def setup_di() -> AsyncContainer:
    providers = setup_providers()
    providers += [JwtProvider(), FastapiProvider(), MongoProvider(), RedisProvider(), WebSocketProvider()]

    container = make_async_container(*providers)

    return container
