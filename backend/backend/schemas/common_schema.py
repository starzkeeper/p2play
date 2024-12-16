import enum
import time

from pydantic import BaseModel, Field


class MetaEnum(enum.EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(enum.Enum, metaclass=MetaEnum):
    pass


class ChannelTypes(str, BaseEnum):
    LOBBY = 'lobby'
    MATCH = 'match'
    USER = 'user'
    ACCEPTANCE = 'acceptance'


class Message(BaseModel):
    action: BaseEnum
    message: str | None
    type: ChannelTypes
    timestamp: int = Field(default_factory=lambda: int(time.time()))
