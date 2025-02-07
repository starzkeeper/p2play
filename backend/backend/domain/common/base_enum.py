import enum


class MetaEnum(enum.EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseStrEnum(enum.StrEnum, metaclass=MetaEnum):
    pass
