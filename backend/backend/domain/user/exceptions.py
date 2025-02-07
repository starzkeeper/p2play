from backend.domain.common.exceptions import DomainException


class EmailError(DomainException):
    pass


class PasswordLengthError(DomainException):
    """Ошибка: длина пароля слишком короткая."""
    pass


class PasswordMissingLowercaseError(DomainException):
    """Ошибка: в пароле отсутствуют строчные буквы."""
    pass


class PasswordMissingUppercaseError(DomainException):
    """Ошибка: в пароле отсутствуют заглавные буквы."""
    pass


class PasswordMissingDigitError(DomainException):
    """Ошибка: в пароле отсутствуют цифры."""
    pass
