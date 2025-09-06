from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.auth import verify_token

EXCLUDED_PATH = ["/api/auth"]


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(prefix) for prefix in EXCLUDED_PATH):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            token_info = verify_token(token)
            request.state.email = token_info.email
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token is required"
            )

        return await call_next(request)
