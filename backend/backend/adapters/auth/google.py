from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from backend.adapters.persistence.settings import google_settings

config_data = {'GOOGLE_CLIENT_ID': google_settings.GOOGLE_CLIENT, 'GOOGLE_CLIENT_SECRET': google_settings.GOOGLE_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)
