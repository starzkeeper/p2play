from datetime import timedelta

from fastapi import HTTPException
from jose import jwt, JWTError
from starlette import status
from starlette.requests import Request

from backend.core.settings import settings
from backend.repositories.user_repository import UserRepository
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus
from backend.schemas.user_schema import UserCreate, UserAuth
from backend.utils.auth import get_password_hash, verify_password, create_access_token, generate_random_password, \
    create_refresh_token
from backend.utils.steam import SteamOID


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, user_data: UserCreate) -> DefaultApiResponse:
        try:
            user = await self.user_repository.find_one_or_none(user_data.email)

            if user:
                return DefaultApiResponse(
                    status=ApiStatus.ERROR,
                    message='User already exists',
                )
            user_dict = user_data.model_dump()
            user_dict['password'] = get_password_hash(user_data.password)

            await self.user_repository.add(**user_dict)
            return DefaultApiResponse(
                status=ApiStatus.SUCCESS,
                message='User created',
            )
        except Exception as e:
            return DefaultApiResponse(
                status=ApiStatus.ERROR,
                message='Something went wrong',
            )

    async def authenticate_user(self, user_data: UserAuth) -> DefaultApiResponse:
        user = await self.user_repository.find_one_or_none(user_data.email)
        if not user or verify_password(plain_password=user_data.password,
                                       hashed_password=user.password) is False:
            return DefaultApiResponse(
                status=ApiStatus.ERROR,
                message='Invalid credentials',
            )

        access_token = create_access_token(data={'sub': str(user.id)})
        refresh_token = create_refresh_token(data={'sub': str(user.id)})
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message={'access_token': access_token, 'refresh_token': refresh_token},
        )

    @staticmethod
    async def get_steam_authorization_url() -> DefaultApiResponse:
        try:
            steam_openid_url = SteamOID.create_url()
            return DefaultApiResponse(
                status=ApiStatus.SUCCESS,
                message=steam_openid_url,
            )
        except Exception as e:
            return DefaultApiResponse(
                status=ApiStatus.ERROR,
                message='Something went wrong'
            )

    async def validate_steam_auth(self, callback_data: Request, user_id: int) -> DefaultApiResponse:
        try:
            callback_data = callback_data.query_params
            result = SteamOID.validate_response(callback_data)
            if result:
                await self.user_repository.insert_steam_id(steam_id=int(result), user_id=user_id)
                return DefaultApiResponse(
                    status=ApiStatus.SUCCESS,
                    message=result,
                )
            else:
                return DefaultApiResponse(
                    status=ApiStatus.ERROR,
                    message='Something went wrong'
                )
        except Exception as e:
            return DefaultApiResponse(
                status=ApiStatus.ERROR,
                message='Something went wrong'
            )

    @staticmethod
    async def validate_refresh_token(refresh_token: str) -> DefaultApiResponse:
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token is invalid!')

        user_id = payload.get('sub')
        token_type = payload.get('token_type')
        if token_type != 'refresh':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token is invalid!')
        access_token = create_access_token(data={'sub': str(user_id)})
        refresh_token = create_refresh_token(data={'sub': str(user_id)})
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message={'access_token': access_token, 'refresh_token': refresh_token},
        )

    async def google_auth(self, user_google: dict) -> DefaultApiResponse:
        user = await self.user_repository.find_one_or_none(user_google['email'])
        if not user:
            user_data = UserCreate(email=user_google['email'], password=generate_random_password())
            user_dict = user_data.model_dump()
            user_dict['password'] = get_password_hash(user_data.password)
            user_dict['is_verified'] = True
            user = await self.user_repository.add(**user_dict)
        if not user.is_verified:
            user.is_verified = True
            await self.user_repository.update(user)

        access_token = create_access_token(data={'sub': str(user.id)})
        refresh_token = create_refresh_token(data={'sub': str(user.id)})
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message={'access_token': access_token, 'refresh_token': refresh_token}
        )
