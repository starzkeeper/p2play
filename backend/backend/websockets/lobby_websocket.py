from typing import List, Dict
from uuid import uuid4

from starlette.websockets import WebSocket


class Lobby:
    def __init__(self, owner_id: int):
        self.lobby_id = str(uuid4())
        self.owner_id= owner_id
        self.players: List[int] = []  # Владелец сразу добавляется
        self.is_open = True  # TODO: закрывать когда никого нет
        self.connections: List[WebSocket] = []  # Активные вебсокет-подключения

    def add_player(self, user_id: int) -> bool:
        if not self.is_open or len(self.players) >= 5 or user_id in self.players:
            return False
        self.players.append(user_id)
        return True

    def remove_player(self, user_id: int):
        if user_id in self.players:
            self.players.remove(user_id)
        if not self.players:  # Если игроков больше нет, закрываем лобби
            self.is_open = False

    async def broadcast(self, message: dict):
        for connection in self.connections:
            # try:
                await connection.send_json(message)
            # except:
            #     self.connections.remove(connection)  # Удаляем разорванное соединение


# TODO: connect with redis
lobbies: Dict[str, Lobby] = {}
