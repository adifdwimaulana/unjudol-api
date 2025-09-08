import uuid
from logging import getLogger
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from playwright.async_api import async_playwright, Page

from app.core.database import get_session
from app.models.job import StartJob, Job, Action, JobStatus
from app.services.comment import CommentService
from app.utils.job import get_video_type

logger = getLogger(__name__)

async def _scroll_page(page: Page, delay_ms: int = 1200) -> None:
    await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(delay_ms)

async def _extract_thread_comment(thread) -> Optional[dict]:
    try:
        text = (await thread.locator("#content-text").inner_text(timeout=2500)).strip()
        if not text:
            return None
    except Exception:
        return None

    # Best-effort metadata
    try:
        author = (await thread.locator("#author-text").inner_text(timeout=1500)).strip()
    except Exception:
        author = None

    try:
        published = (await thread.locator("#header-author yt-formatted-string.published-time-text > a")
                     .inner_text(timeout=1500)).strip()
    except Exception:
        published = None

    try:
        like_txt = (await thread.locator("#vote-count-middle").inner_text(timeout=1500)).strip()
        likes = int(like_txt.replace(",", "")) if like_txt else 0
    except Exception:
        likes = 0

    # Prefer existing element tag, else generate
    try:
        el_id = await thread.get_attribute("data-comment-id")
    except Exception:
        el_id = None
    if not el_id:
        el_id = str(uuid.uuid4())
        try:
            await thread.evaluate("(el, id) => el.setAttribute('data-comment-id', id)", el_id)
        except Exception:
            pass

    return {
        "id": el_id,
        "author": author,
        "comment": text,
        "published_time": published,
        "likes": likes,
    }

async def scrape_comment_from_video(url: str):
    comments: list[dict] = []
    seen_ids = set()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=5*1000) # timeout=5s

            # 1. Scroll page until comment section appears
            # await page.mouse.wheel(0, 2000)
            # await page.wait_for_timeout(2000)
            await page.wait_for_timeout(2000)
            await page.evaluate("() => window.scrollBy(0, window.innerHeight)")

            try:
                await page.wait_for_selector("ytd-comments#comments, #comments", timeout=15000)
            except Exception:
                logger.error("Couldn't mount ytd-comments#comments")
                pass

            # 2. Populate comments
            thread_els = page.locator("ytd-comment-thread-renderer")
            last_count = 0
            stagnant_rounds = 0
            MAX_STAGNANT = 0

            while True:
                await _scroll_page(page, delay_ms=1200)

                current_count = await thread_els.count()

                if current_count > last_count:
                    for i in range(last_count, current_count):
                        thread = thread_els.nth(i)
                        data = await _extract_thread_comment(thread)

                        if not data:
                            continue
                        if data["id"] in seen_ids:
                            continue

                        comments.append(data)
                        seen_ids.add(data["id"])

                        print("comment", data)

            # await page.wait_for_timeout(2000)
            # await page.evaluate("() => window.scrollBy(0, window.innerHeight)")

            # comment_el = page.locator("ytd-comments#comments")
            # await comment_el.wait_for()
            # print(comment_el)
            #
            # # 2. Populate comments
            # thread_els = page.locator("ytd-comment-thread-renderer")
            # visible_thread_count = await thread_els.count()
            # print("threads", thread_els, "count", visible_thread_count)
            #
            # for i in range(visible_thread_count):
            #     current_thread = thread_els.nth(i)
            #     print("current thread", current_thread)
            #
            #     try:
            #         comment_el = page.locator("#content-text")
            #         comment = await comment_el.inner_text()
            #         comment = comment.strip()
            #         print("comment", comment)
            #     except Exception:
            #         continue
            #
            #
            # time.sleep(10)

            # Check Video Ownership
            # avatar_btn =


            # context = await browser.new_context(
            #     viewport={"width": 1920, "height": 1080}
            # )
            # page = await context.new_page()
            #
            # page.goto(url)
            #
            # time.sleep(5)
            # page.close()
        finally:
            await browser.close()

    pass

class JobService:
    def __init__(self, comment_service: Annotated[CommentService, Depends(CommentService)], session: AsyncSession = Depends(get_session)):
        self.s = session
        self.comment_service = comment_service

    async def scrape(self, data: StartJob):
        url = data.url

        if not url.startswith("https://www.youtube.com"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid YouTube URL")

        job = Job(action=Action.SCRAPE, url=url, type=get_video_type(data.url), status=JobStatus.STARTED)

        # self.s.add(job)
        # await self.s.commit()
        # await self.s.refresh(job)
        await scrape_comment_from_video(data.url)

        # print("start")
        # time.sleep(10)
        # print("finish")
        return

    async def remove(self):
        return