from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., description="The password must be from 5 to 50 characters", min_length=5, max_length=50)


class UserAuth(BaseModel):
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=5, max_length=50, description="The password must be from 5 to 50 characters")


class FriendshipStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
