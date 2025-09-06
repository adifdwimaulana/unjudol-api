from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import config

engine: AsyncEngine = create_async_engine(config.DATABASE_URI, echo=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = SessionLocal()
    try:
        yield session
    finally:
        await session.close()
