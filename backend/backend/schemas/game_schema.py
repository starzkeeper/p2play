from backend.schemas.common_schema import BaseEnum


class Game(str, BaseEnum):
    DUST2 = 'dust2'