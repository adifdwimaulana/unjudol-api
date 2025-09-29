from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from openai import OpenAI

from app.core.database import get_session
from app.models.comment import GetCommentQuery, GetComment, Comment, CheckComment
from app.models.common import BaseListResponse
from app.core.config import config


class CommentService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.s = session
        self.openai = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url="https://api.deepseek.com"
        )

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
    
    async def check_comment(self, request: CheckComment):
        prompt = """
            Kamu adalah asisten untuk mengidentifikasi komentar YouTube yang mengandung kata-kata atau website judi online
            1. Website judi online biasanya menggunakan campuran alphanumeric dan special character untuk menghindari censorship,
                seperti: alexis17, P U L A U W I N, 𝐒𝐆𝐈𝟖𝟖, 𝐀𝐋EXIS17, 𝒫𝒰𝐿𝒜𝒰𝟩𝟩𝟩, А 𝙓 𝐋 7 𝟳 𝟩, GA RU DA HO KI, 𝗞𝗢𝗜𝗦𝗟𝗢𝗧
            2. Komentar judi online biasanya berisikan beberapa keyword seperti jackpot, WD, gacor, hoki, slot, menang.
            3. PENTING: dari class CheckComment, return list of id tentang komentar yang kemungkinan mengandung kata-kata atau website judi online
            4. Tidak perlu kalimat lain. Hanya return list of id saja (dalam int), contoh [1] atau [1,2,3]
            5. Jika semua komentar tidak mengandung judi online return empty array []
        
            response: [1, 2, 3]
        """

        messages = [
            { "role": "system", "content": prompt },
            {
                "role": "user",
                "content": f"Identifikasi komentar mengandung judi online: {request.comments}",
            },
        ]

        try:
            chat = self.openai.chat.completions.create(
                model="deepseek-chat",
                temperature=0,
                messages=messages
            )
            response = chat.choices[0].message.content

            if not response:
                raise ValueError("No response from OpenAI")
            
            ids = eval(response)  # Using eval to parse the list from string
            if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
                raise ValueError("Invalid response format from OpenAI")
            
            return ids
        except Exception as e:
            raise e
