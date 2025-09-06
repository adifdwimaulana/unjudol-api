from typing import Generic, TypeVar, List

from sqlmodel import SQLModel

T = TypeVar("T")

class MessageResponse(SQLModel):
    message: str

class BasePagination(SQLModel):
    page: int = 0
    size: int = 10

class BaseListResponse(SQLModel, Generic[T]):
    content: List[T]
    total: int
