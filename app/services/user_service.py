from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.models.user import User, CreateUser, GetUser


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.s = session

    async def get_user_by_email(self, email: str) -> User:
        user = await self.s.scalar(select(User).where(User.email == email))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    async def create_user(self, data: CreateUser) -> GetUser:
        user = self.get_user_by_email(data.email)

        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exist"
            )

        new_user = User(**data.model_dump())
        self.s.add(new_user)
        await self.s.commit()
        await self.s.refresh(new_user)
        return GetUser.model_validate(new_user, from_attributes=True)
