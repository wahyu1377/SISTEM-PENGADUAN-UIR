"""
Pytest configuration and fixtures.
"""
import pytest
import asyncio
from typing import Generator

from app.core.config import settings

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_settings():
    """Provide test settings."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
