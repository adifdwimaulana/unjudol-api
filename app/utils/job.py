import uuid
import re
from urllib.parse import  urlparse, parse_qs
from fastapi import HTTPException, status

from app.models.job import Type
from playwright.async_api import Page

SHORTS = "/shorts/"
LONG_TIMEOUT = 30000
SHORT_TIMEOUT = 5000

# Locator
COMMENT_SECTION = "ytd-comments#comments"
UNSEEN_COMMENT = "ytd-comment-thread-renderer #content-text:not([data-comment-id])"
VISIBLE_COMMENT = "ytd-comment-thread-renderer #content-text"


def get_video_type(url: str) -> Type:
    if SHORTS in url:
        return Type.SHORT
    return Type.VIDEO

def normalize_url(url: str) -> str:
    if not url.startswith("https://www.youtube.com"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid YouTube URL")

    if get_video_type(url) == Type.SHORT:
        parsed_url = re.search(r"/shorts/([A-Za-z0-9_-]+)", url)
        video_id = parsed_url.group(1)
        return f"https://www.youtube.com/watch?v={video_id}"

    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query)
    video_id = qs.get("v", [None])[0]
    return f"https://www.youtube.com/watch?v={video_id}"

async def go_to_and_wait(page: Page, url: str):
    await page.goto(url, wait_until="domcontentloaded", timeout=LONG_TIMEOUT)
    await page.wait_for_timeout(SHORT_TIMEOUT)

async def scroll_to_comments(page: Page):
    comments = page.locator(COMMENT_SECTION)

    await page.evaluate("() => window.scrollBy(0, window.innerHeight)")
    await comments.wait_for(state="visible", timeout=LONG_TIMEOUT)
    await comments.scroll_into_view_if_needed()
    await page.wait_for_timeout(SHORT_TIMEOUT)

async def collect_comments(page: Page) -> list[str]:
    nodes = page.locator(UNSEEN_COMMENT)
    handles = await nodes.element_handles()
    comments: list[str] = []

    for handle in handles:
        if not handle:
            continue

        text = await handle.inner_text()
        text = text.strip()

        # Assign id to viewed comments
        try:
            await handle.evaluate("(el, id) => el.setAttribute('data-comment-id', id)", str(uuid.uuid4()))
        except Exception:
            pass

        comments.append(text)

    return comments

async def infinite_scroll(page: Page, max_comment: int, max_stall_round: int = 3):
    results: list[str] = []
    stall_round = 0
    last_visible_count = -1

    while True:
        comment_per_batch = await collect_comments(page)
        results.extend(comment_per_batch)

        if len(results) > max_comment:
            break

        visible_count = await page.locator(VISIBLE_COMMENT).count()

        if visible_count <= last_visible_count:
            stall_round += 1
        else:
            stall_round = 0
            last_visible_count = visible_count

        if stall_round >= max_stall_round:
            break

        # Scroll to load new comments
        await page.evaluate("() => window.scrollBy(0, document.documentElement.scrollHeight)")
        await page.wait_for_timeout(SHORT_TIMEOUT)

        # If nothing matches new comment, increase stall_round
        unseen_comment = await page.locator(UNSEEN_COMMENT).count()
        if unseen_comment == 0:
            stall_round += 1

    return results[:max_comment]