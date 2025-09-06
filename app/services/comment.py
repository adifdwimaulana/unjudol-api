from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func

from app.core.database import get_session
from app.models.comment import GetCommentQuery, GetComment, Comment
from app.models.common import BaseListResponse


class CommentService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.s = session

    async def get_comment(self, query: GetCommentQuery) -> BaseListResponse[GetComment]:
        statement = select(Comment)
        if query.url:
            statement = statement.where(Comment.url == query.url)
        if query.label:
            statement = statement.where(Comment.label == query.label)
        if query.job_id:
            statement = statement.where(Comment.job_id == query.job_id)

        total_statement = select(func.count()).select_from(statement.subquery())
        total = await self.s.exec(total_statement)
        total = total.one()

        offset = query.page * query.size
        statement = statement.offset(offset).limit(query.size)

        result = await self.s.exec(statement)
        content = [GetComment.model_validate(row, from_attributes=True) for row in result.all()]

        return BaseListResponse[GetComment](
            content=content,
            total=total
        )
