from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException

from app.models.message import MessageResponse
from app.models.user import CreateUser, UserToken, UserLogin
from app.services.auth import AuthService, create_access_token
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(path="/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data: CreateUser, user_service: Annotated[UserService, Depends(UserService)]) -> MessageResponse:
    await user_service.create_user(data)
    return MessageResponse(message="user successfully registered")

@router.post(path="/token", response_model=UserToken, status_code=status.HTTP_200_OK)
async def login(data: UserLogin, auth_service: Annotated[AuthService, Depends(AuthService)]) -> UserToken:
    user = await auth_service.authenticate_user(data.email, data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized"
        )

    encoded_token = create_access_token(data={"sub": user.email})
    return UserToken(access_token=encoded_token)
