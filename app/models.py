from sqlmodel import Field, SQLModel
from app.schemas import UserBase

import uuid

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
