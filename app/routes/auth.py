from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.user import GetUser, CreateUser
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

async def register_user(data: CreateUser, user_service: Annotated[UserService, Depends(UserService)]) -> GetUser:
    return await user_service.create_user(data)

