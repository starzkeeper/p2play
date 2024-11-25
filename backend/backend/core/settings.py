import configparser
from pydantic_settings import BaseSettings

__CFG_FILENAME__ = "/app/backend/config.ini"


class MetaConfig(type):
    _file_path: str = __CFG_FILENAME__

    @property
    def get_value(cls, ):
        if getattr(cls, '_conf', None) is None:
            cls._conf = configparser.ConfigParser()
            cls._conf.read(cls._file_path)
        return cls._conf

    @get_value.setter
    def change_config_file(cls, new_file_path: str = None):
        cls._file_path = new_file_path


class ConfigManager(metaclass=MetaConfig):
    pass


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = ConfigManager.get_value['JWT']['SECRET_KEY']
    ALGORITHM: str = ConfigManager.get_value['JWT']['ALGORITHM']
    ACCESS_TOKEN_EXPIRES: int = int(ConfigManager.get_value['JWT']['ACCESS_TOKEN_EXPIRES'])
    REFRESH_TOKEN_EXPIRES: int = int(ConfigManager.get_value['JWT']['REFRESH_TOKEN_EXPIRES'])

    # REDIS
    REDIS_HOST: str = ConfigManager.get_value['REDIS']['REDIS_HOST']
    REDIS_PORT: int = int(ConfigManager.get_value['REDIS']['REDIS_PORT'])

    # GOOGLE
    GOOGLE_CLIENT: str = ConfigManager.get_value['GOOGLE']['GOOGLE_CLIENT']
    GOOGLE_SECRET: str = ConfigManager.get_value['GOOGLE']['GOOGLE_SECRET']

    # SERVER
    SERVER_URL: str = ConfigManager.get_value['SERVER']['SERVER_URL']


settings = Settings()
