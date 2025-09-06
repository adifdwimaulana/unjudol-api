import bcrypt
from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from bcrypt import hashpw

from app.core.database import get_session
from app.models.user import User, CreateUser, GetUser

class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.s = session

    async def get_user_by_email(self, email: str) -> User:
        return await self.s.scalar(select(User).where(User.email == email))

    async def create_user(self, data: CreateUser) -> GetUser:
        user = await self.get_user_by_email(data.email)

        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="user already exist"
            )

        hashed_password = hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        new_user = User(**data.model_dump())
        new_user.password = hashed_password
        self.s.add(new_user)
        await self.s.commit()
        await self.s.refresh(new_user)
        return GetUser.model_validate(new_user, from_attributes=True)
