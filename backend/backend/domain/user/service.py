import re

from backend.domain.user.exceptions import PasswordLengthError, PasswordMissingLowercaseError


def validate_password(password: str) -> None:
    """
    Валидирует пароль и выбрасывает исключения, если пароль не соответствует требованиям.
    """
    # if len(password) < 8:
    #     raise PasswordLengthError

    if not re.search(r"[a-z]", password):
        raise PasswordMissingLowercaseError

    # if not re.search(r"[A-Z]", password):
    #     raise PasswordMissingUppercaseError
    #
    # if not re.search(r"\d", password):
    #     raise PasswordMissingDigitError