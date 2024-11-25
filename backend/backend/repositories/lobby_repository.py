import json
from uuid import uuid4

from redis.asyncio import Redis
from starlette.websockets import WebSocket, WebSocketState

from backend.schemas.lobby_schema import LobbyMessage


class LobbyRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.pubsub = redis_client.pubsub()

    async def create_lobby(self):
        lobby_id = str(uuid4())
        data = {
            "owner_id": json.dumps(None),
            "players": json.dumps([]),
        }
        await self.redis_client.hset(f"lobby_{lobby_id}", mapping=data)
        return lobby_id

    async def get_lobby(self, lobby_id) -> bool:
        exists = await self.redis_client.exists(f"lobby_{lobby_id}")
        return exists > 0

    async def add_player(self, lobby_id: str, user_id: int) -> bool:
        lobby = await self.redis_client.hgetall(f"lobby_{lobby_id}")
        players = json.loads(lobby.get('players', '[]'))
        if len(players) >= 5 or user_id in players:
            return False

        players.append(user_id)
        updates = {"players": json.dumps(players)}
        if len(players) == 1:
            updates["owner_id"] = user_id

        await self.redis_client.hset(f"lobby_{lobby_id}", mapping=updates)
        return True

    async def subscribe_to_lobby(self, lobby_id: str):
        await self.pubsub.subscribe(f"lobby_channel_{lobby_id}")
        return self.pubsub

    async def read_pubsub_messages(self, pubsub, websocket: WebSocket):
        while True:
            if websocket.client_state == WebSocketState.DISCONNECTED:
                break
            message = await pubsub.get_message(ignore_subscribe_messages=True)

            if message:
                await websocket.send_text(message['data'])

    async def publish_message(self, lobby_id: str, message: LobbyMessage):
        await self.redis_client.publish(f"lobby_channel_{lobby_id}", message.model_dump_json())

    async def remove_player(self, lobby_id: str, user_id: int):
        lobby = await self.redis_client.hgetall(f"lobby_{lobby_id}")
        players = json.loads(lobby.get('players', '[]'))
        owner_id = int(lobby.get('owner_id', '0'))

        if user_id not in players:
            return

        players.remove(user_id)

        if players:
            await self.redis_client.hset(f"lobby_{lobby_id}", "players", json.dumps(players))

            if owner_id == user_id:
                new_owner_id = players[0]
                await self.redis_client.hset(f"lobby_{lobby_id}", "owner_id", new_owner_id)
        else:
            await self.redis_client.delete(f"lobby_{lobby_id}")

    async def all_lobbies(self):
        lobbies = await self.redis_client.keys()
        return lobbies



