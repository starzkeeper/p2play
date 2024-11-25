import secrets
import string

from passlib.context import CryptContext
from jose import jwt
from datetime import timedelta

from backend.core.settings import settings
from backend.db.models.base import now_utc

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRES)) -> str:
    to_encode = data.copy()
    expire = now_utc() + expires_delta
    to_encode.update({"exp": expire, 'token_type': 'access'})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encode_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(seconds=settings.REFRESH_TOKEN_EXPIRES)) -> str:
    to_encode = data.copy()
    expire = now_utc() + expires_delta
    to_encode.update({"exp": expire, 'token_type': 'refresh'})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encode_jwt


def generate_random_password(min_length=5, max_length=50):
    length = secrets.choice(range(min_length, max_length + 1))

    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))
