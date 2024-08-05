import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import database_exists, drop_database

from alembic import command
from alembic.config import Config


def configure_test_environment():
    """Set up the environment for testing."""
    os.environ["ENV_STATE"] = "TEST"


# Configure the test environment before importing application components
configure_test_environment()

# Import application components after configuring the environment
from app.core import database  # noqa
from app.main import app  # noqa


def setup_database():
    """Set up the test database by applying migrations."""
    from app.settings.config import settings

    uri = settings.DATABASE_URL

    if database_exists(uri):
        drop_database(uri)

    config = Config("alembic.ini")
    command.upgrade(config, "head")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    setup_database()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in database.provide_session():
        yield session


@pytest.fixture(scope="function")
async def db_transaction() -> AsyncGenerator[AsyncSession, None]:
    async for session in database.provide_transaction():
        yield session


@pytest.fixture
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac
