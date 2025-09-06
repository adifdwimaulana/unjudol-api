from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine, create_async_engine

from app.core.config import config

engine: AsyncEngine = create_async_engine(config.DATABASE_URI, echo=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = SessionLocal()
    try:
        yield session
    finally:
        await session.close()
