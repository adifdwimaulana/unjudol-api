from enum import Enum
from sqlmodel import SQLModel, Field

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class UserBase(SQLModel):
    email: str = Field(primary_key=True)
    name: str
    role: UserRole = Field(default=UserRole.USER, nullable=False)

class User(UserBase, table=True):
    __tablename__ = "user"
    password: str

class CreateUser(UserBase):
    password: str

class GetUser(UserBase):
    pass

class UserToken(SQLModel):
    access_token: str

class TokenInfo(SQLModel):
    email: str
