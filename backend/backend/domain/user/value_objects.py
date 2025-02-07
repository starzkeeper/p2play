import re
from dataclasses import dataclass

from backend.domain.user.exceptions import EmailError


@dataclass(frozen=True, slots=True, eq=True, unsafe_hash=True)
class EmailField:
    email: str

    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    def __post_init__(self):
        if not re.match(self.EMAIL_REGEX, self.email):
            raise EmailError(f"Invalid email format: {self.email}")

    def __str__(self) -> str:
        return self.email
