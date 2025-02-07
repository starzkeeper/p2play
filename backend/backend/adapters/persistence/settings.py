import configparser
from pydantic_settings import BaseSettings
from pydantic import BaseModel

__CFG_FILENAME__ = "/app/backend/config.ini"


class MetaConfig(type):
    _file_path: str = __CFG_FILENAME__
    _conf = None

    @property
    def get_value(cls, ):
        if getattr(cls, '_conf', None) is None:
            cls._conf = configparser.ConfigParser()
            cls._conf.read(cls._file_path)
        return cls._conf

    @get_value.setter
    def change_config_file(cls, new_file_path: str = None):
        cls._file_path = new_file_path
        cls._conf = None


class ConfigManager(metaclass=MetaConfig):
    pass


class Settings(BaseSettings):
    # SERVER
    SERVER_URL: str = ConfigManager.get_value['SERVER']['SERVER_URL']


class JwtSettings(BaseSettings):
    SECRET_KEY: str = ConfigManager.get_value['JWT']['SECRET_KEY']
    ALGORITHM: str = ConfigManager.get_value['JWT']['ALGORITHM']
    ACCESS_TOKEN_EXPIRES: int = int(ConfigManager.get_value['JWT']['ACCESS_TOKEN_EXPIRES'])
    REFRESH_TOKEN_EXPIRES: int = int(ConfigManager.get_value['JWT']['REFRESH_TOKEN_EXPIRES'])


class RedisSettings(BaseSettings):
    REDIS_HOST: str = ConfigManager.get_value['REDIS']['REDIS_HOST']
    REDIS_PORT: int = int(ConfigManager.get_value['REDIS']['REDIS_PORT'])


class GoogleSettings(BaseSettings):
    GOOGLE_CLIENT: str = ConfigManager.get_value['GOOGLE']['GOOGLE_CLIENT']
    GOOGLE_SECRET: str = ConfigManager.get_value['GOOGLE']['GOOGLE_SECRET']


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "p2play"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"  # INFO prod

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },

    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


settings = Settings()
jwt_settings = JwtSettings()
redis_settings = RedisSettings()
google_settings = GoogleSettings()

