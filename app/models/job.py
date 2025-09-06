import uuid

from typing import Optional
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field

class JobStatus(str, Enum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class JobBase(SQLModel):
    action: str = Field(index=True, nullable=False)
    url: str
    type: str = Field(index=True)
    status: JobStatus = Field(default=JobStatus.STARTED)
    started_at: datetime = Field(default_factory=datetime.now, nullable=False)
    completed_at: Optional[datetime]

class Job(JobBase, table=True):
    __tablename__ = "job"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    created_by: str = Field(default='system')
    last_updated_at = Optional[datetime]
    last_updated_by = Optional[str]

class CreateJob(JobBase):
    pass

class GetJob(JobBase):
    id: uuid.UUID
