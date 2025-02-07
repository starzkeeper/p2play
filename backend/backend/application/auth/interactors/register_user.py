from dataclasses import dataclass

from backend.application.common.interactor import Interactor
from backend.application.common.password import get_password_hash
from backend.application.errors.user import UserAlreadyExists
from backend.application.users.gateway import UserSaver, UserReader
from backend.domain.user.models import User
from backend.domain.user.service import validate_password
from backend.domain.user.value_objects import EmailField


@dataclass
class RegisterUserDTO:
    email: EmailField
    password: str
    nickname: str


class Register(Interactor[RegisterUserDTO, None]):
    def __init__(
            self,
            user_saver: UserSaver,
            user_reader: UserReader,
    ) -> None:
        self.user_saver = user_saver
        self.user_reader = user_reader

    async def __call__(self, data: RegisterUserDTO) -> None:
        validate_password(data.password)
        user = await self.user_reader.find_one_or_none(data.email)

        if user:
            raise UserAlreadyExists

        data.password = get_password_hash(data.password)

        user_instance = User(
            email=data.email,
            password=data.password,
            nickname=data.nickname,
        )

        await self.user_saver.create_user(user_instance)
