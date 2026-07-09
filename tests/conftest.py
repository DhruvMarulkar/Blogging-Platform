import os
from collections.abc import AsyncGenerator

os.environ["DATAbase_URL"] = (
    "postgresql+psycopg://bloguser:blogpass@localhost/test_blog"
)
os.environ["S3_BUCKET_NAME"] = "test-bucket"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

os.environ["S3_ACCESS_KEY_ID"] = "testing"
os.environ["S3_SECRET_ACCESS_KEY"] = "testing"
os.environ["S3_REGION"] = "ap-south-1"

os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "ap-south-1"

import boto3
import pytest
from httpx import ASGITransport, AsyncClient
from moto import mock_aws
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from database import base, get_db
from main import app

pytest_plugins = ["anyio"]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        os.environ["DATAbase_URL"],
        poolclass=NullPool,
    )
    return engine


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def db_session(
    test_engine,
    setup_database,
) -> AsyncGenerator[AsyncSession]:
    conn = await test_engine.connect()
    trans = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()


@pytest.fixture
def mocked_aws():
    with mock_aws():
        s3 = boto3.client(
            "s3",
            region_name="ap-south-1",
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )

        s3.create_bucket(
            Bucket=os.environ["S3_BUCKET_NAME"],
            CreateBucketConfiguration={
                "LocationConstraint": "ap-south-1",
            },
        )

        yield s3


@pytest.fixture
async def client(
    db_session: AsyncSession,
    mocked_aws,
) -> AsyncGenerator[AsyncClient]:

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> dict:
    response = await client.post(
        "/api/users",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> str:
    response = await client.post(
        "/api/users/token",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}