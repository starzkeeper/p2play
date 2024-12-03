import json
from uuid import uuid4

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from backend.schemas.lobby_schema import LobbyMessage, Sender


class LobbyRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client: Redis = redis_client
        self.pubsub: PubSub = redis_client.pubsub()

    async def set(self, key: str, value: str):
        await self.redis_client.set(key, value)

    async def get(self, key: str):
        return await self.redis_client.get(key)

    async def hgetall(self, key: str):
        return await self.redis_client.hgetall(key)

    async def exists(self, key: str):
        return await self.redis_client.exists(key)

    async def create_lobby(self, user_id: int):
        lobby_id = str(uuid4())
        data = {
            "owner_id": user_id,
            "players": json.dumps([user_id]),
        }
        await self.redis_client.hset(f"lobby_{lobby_id}", mapping=data)
        return lobby_id

    async def get_lobby(self, lobby_id) -> bool:
        exists = await self.redis_client.get(f"lobby_{lobby_id}")
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
        await self.redis_client.set(f"user:{user_id}:lobby_id", lobby_id)
        return True

    async def subscribe_to(self, channel_name: str):
        await self.pubsub.subscribe(channel_name)
        return self.pubsub

    async def unsubscribe_from(self, channel_name: str):
        await self.pubsub.unsubscribe(channel_name)

    async def get_message(self, pubsub: PubSub):
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        return message

    async def publish_message(self, channel_name: str, message: LobbyMessage, sender: Sender):
        message_dict = message.model_dump()
        message_dict['sender'] = sender
        await self.redis_client.publish(channel_name, json.dumps(message_dict))

    async def remove_player(self, lobby_id: str, user_id: int):
        lobby = await self.redis_client.hgetall(f"lobby_{lobby_id}")
        players = json.loads(lobby.get('players', '[]'))
        owner_id = int(lobby.get('owner_id', '0'))

        if user_id not in players:
            return

        players.remove(user_id)
        await self.redis_client.delete(f"user:{user_id}:lobby_id")

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




