import uuid

from typing import Optional
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Enum as SAEnum, Column

class JobStatus(str, Enum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Type(str, Enum):
    VIDEO = "VIDEO"
    SHORT = "SHORT"

class Action(str, Enum):
    SCRAPE = "SCRAPE"
    REMOVE = "REMOVE"

class JobBase(SQLModel):
    url: str
    action: Action = Field(
        sa_column=Column(
            SAEnum(Action, name="action", native_enum=False),
            index=True,
            nullable=False
        )
    )
    type: Type = Field(
        sa_column=Column(
            SAEnum(Type, name="type", native_enum=False),
            index=True,
            nullable=False
        )
    )
    status: JobStatus = Field(
        sa_column=Column(
            SAEnum(JobStatus, name="job_status", native_enum=False),
            index=True,
            nullable=False,
            default=JobStatus.STARTED
        )
    )
    started_at: datetime = Field(default_factory=datetime.now, nullable=False)
    completed_at: Optional[datetime]

class Job(JobBase, table=True):
    __tablename__ = "job"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    created_by: str = Field(default='system')
    last_updated_at: Optional[datetime]
    last_updated_by: Optional[str]

class GetJob(JobBase):
    id: uuid.UUID
    status: JobStatus = Field(default=JobStatus.STARTED)
    started_at: datetime = Field(default_factory=datetime.now, nullable=False)
    completed_at: Optional[datetime]

class StartJob(SQLModel):
    url: str