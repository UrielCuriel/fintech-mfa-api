from typing import Annotated, Literal
from pydantic import EmailStr
from sqlmodel import SQLModel, Field


import uuid
from typing import Optional


class Token(SQLModel):
    access_token: Optional[str] = None
    temp_token: Optional[str] = None
    requires_totp: bool = False
    message: Optional[str] = None
    token_type: Literal["bearer", "temp_totp"] = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: Annotated[bool, Field(default=True, exclude=True)]
    is_superuser: Annotated[bool, Field(default=False, exclude=True)]
    full_name: str | None = Field(default=None, max_length=255)
    otp_enabled: bool = False


class UserPublic(UserBase):
    id: uuid.UUID


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class Message(SQLModel):
    message: str


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class Otp(SQLModel):
    totp_code: str
