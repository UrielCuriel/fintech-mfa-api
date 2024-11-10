from sqlmodel import Field, SQLModel
from app.schemas import UserBase
from sqlalchemy.dialects.postgresql import JSONB
from typing import Dict, Optional

import uuid

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    otp_secret: str | None = Field(default=None) 

