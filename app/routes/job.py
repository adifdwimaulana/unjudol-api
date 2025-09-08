from typing import Annotated

from fastapi import APIRouter, status, Depends, BackgroundTasks

from app.models.common import MessageResponse
from app.models.job import StartJob
from app.services.job import JobService

router = APIRouter(prefix="/jobs", tags=["job"])

@router.post(path="/scrape", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def scrape_job(data: StartJob, background: BackgroundTasks, job_service: Annotated[JobService, Depends(JobService)]):
    background.add_task(job_service.scrape, data=data)
    return MessageResponse(message=f"job started for {data.url}")
