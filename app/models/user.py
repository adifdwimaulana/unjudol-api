from enum import Enum

from sqlmodel import SQLModel, Field, Enum as SAEnum, Column

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class UserBase(SQLModel):
    email: str = Field(primary_key=True)
    name: str

class User(UserBase, table=True):
    __tablename__ = "user"
    role: UserRole = Field(
        sa_column=Column(
            SAEnum(UserRole, name="user_role", native_enum=False),
            default=UserRole.USER,
            index=True,
            nullable=False
        )
    )
    password: str

class CreateUser(UserBase):
    password: str

class GetUser(UserBase):
    pass

class UserLogin(SQLModel):
    email: str
    password: str

class UserToken(SQLModel):
    access_token: str

class TokenInfo(SQLModel):
    email: str
