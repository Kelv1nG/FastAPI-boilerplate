from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.settings.config import settings

engine = create_async_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)

sessionmaker = async_sessionmaker(expire_on_commit=False)


async def provide_transaction() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker(bind=engine) as session:
        async with session.begin():
            yield session


async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker(bind=engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        if engine:
            await engine.dispose()
