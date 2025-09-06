from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from bcrypt import checkpw

from app.core.config import config
from app.models.user import TokenInfo
from app.services.user_service import UserService

SECRET_KEY = config.JWT_SECRET_KEY
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    token_info = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)

    token_info.update({"exp": expire})
    encoded_jwt = jwt.encode(token_info, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_service.get_user_by_email(email)

        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user

    async def decode_token(self, token: Annotated[str, Depends(oauth2_scheme)]):
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            if email is None:
                raise exception
            token_info = TokenInfo(email=email)
        except InvalidTokenError:
            raise exception

        user = await self.user_service.get_user_by_email(token_info.email)
        return user
