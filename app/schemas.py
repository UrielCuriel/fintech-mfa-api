from typing import Literal
from pydantic import EmailStr
from sqlmodel import  SQLModel, Field


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

class TokenData(SQLModel):
    username: str | None = None
    email: EmailStr | None = None
    


class UserBase(SQLModel):
    username: str
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    otp_enabled: bool = False


class UserPublic(UserBase):
    id: uuid.UUID

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)

class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)

class Message(SQLModel):
    message: str

class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
    
    
class Otp(SQLModel):
    totp_code: str
