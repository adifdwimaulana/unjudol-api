from typing import Annotated

from fastapi import APIRouter, status, Depends

from app.models.comment import GetComment, GetCommentQuery
from app.models.common import BaseListResponse
from app.services.comment import CommentService

router = APIRouter(prefix="/comments", tags=["comment"])

@router.get(path="/", response_model=BaseListResponse[GetComment], status_code=status.HTTP_200_OK)
async def get_comment(query: Annotated[GetCommentQuery, Depends()], comment_service: Annotated[CommentService, Depends(CommentService)]) -> BaseListResponse[GetComment]:
    return await comment_service.get_comment(query)
