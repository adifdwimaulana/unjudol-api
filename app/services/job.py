from datetime import datetime
from logging import getLogger
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from playwright.async_api import async_playwright

from app.core.database import get_session
from app.models.job import StartJob, Job, Action, JobStatus
from app.models.comment import Comment
from app.services.comment import CommentService
from app.utils.job import get_video_type, go_to_and_wait, scroll_to_comments, infinite_scroll, normalize_url

logger = getLogger(__name__)

async def scrape_comment_from_video(url: str, max_comment: int):
    async with async_playwright() as pw:
        logger.info("starting job for video %s", url)
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()

            await go_to_and_wait(page, url)
            await scroll_to_comments(page)
            results = await infinite_scroll(page, max_comment=max_comment)
            return results
        finally:
            logger.info("job finish for video %s", url)
            await browser.close()


class JobService:
    def __init__(self, comment_service: Annotated[CommentService, Depends(CommentService)], session: AsyncSession = Depends(get_session)):
        self.s = session
        self.comment_service = comment_service

    async def scrape(self, data: StartJob):
        normalized_url = normalize_url(data.url)

        job = Job(action=Action.SCRAPE, url=normalized_url, type=get_video_type(data.url), status=JobStatus.STARTED)
        self.s.add(job)
        await self.s.commit()
        await self.s.refresh(job)

        try:
            results = await scrape_comment_from_video(url=normalized_url, max_comment=data.max_comment)
            comments = [
                Comment(
                    job_id=job.id,
                    url=normalized_url,
                    content=comment
                ) for comment in results
            ]
            self.s.add_all(comments)

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()

            await self.s.commit()
            await self.s.refresh(job)
            return
        except Exception as e:
            logger.exception("Error while scraping job %s", job.id)
            await self.s.rollback()

            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()

            await self.s.commit()
            await self.s.refresh(job)


    async def remove(self):
        return