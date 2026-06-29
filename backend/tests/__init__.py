"""
Test configuration and fixtures.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.core.database import DatabaseManager

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def test_client():
    """Create a test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db():
    """Create a test database connection."""
    # Use a test database
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    test_db = client["test_uir_complaints"]

    # Store original db
    original_db = DatabaseManager.db

    # Set test db
    DatabaseManager.db = test_db

    yield test_db

    # Cleanup
    await test_db.drop_collection("users")
    await test_db.drop_collection("complaints")
    await test_db.drop_collection("documents")

    # Restore original
    DatabaseManager.db = original_db
