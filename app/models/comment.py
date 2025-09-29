import uuid

from typing import Optional
from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Enum as SAEnum
from pydantic import BaseModel

from app.models.common import BasePagination


class CommentLabel(str, Enum):
    JUDOL = "JUDOL"
    NON_JUDOL = "NON_JUDOL"
    NO_LABEL = "NO_LABEL"

class CommentBase(SQLModel):
    job_id: uuid.UUID
    url: str = Field(index=True, nullable=False)
    label: CommentLabel = Field(
        sa_column=Column(
            SAEnum(CommentLabel, name="label", native_enum=False),
            default=CommentLabel.NO_LABEL,
            index=True,
            nullable=False
        )
    )
    content: str

class Comment(CommentBase, table=True):
    __tablename__ = "comment"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    created_by: str = Field(default='system')
    last_updated_at: Optional[datetime]
    last_updated_by: Optional[str]

class CreateComment(CommentBase):
    pass

class GetComment(CommentBase):
    id: uuid.UUID

class GetCommentQuery(BasePagination):
    job_id: Optional[uuid.UUID] = None
    url: Optional[str] = None
    label: Optional[str] = None

class CommentRequest(BaseModel):
    id: int
    text: str

class CheckComment(BaseModel):
    comments: list[CommentRequest]
