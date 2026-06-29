"""
Tests for authentication module.
"""
import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.auth.service import AuthService
from app.auth.schemas import UserRegister, UserLogin

class TestAuthSchemas:
    """Test authentication schemas."""

    def test_user_register_valid(self):
        """Test valid user registration data."""
        user = UserRegister(
            email="test@example.com",
            name="Test User",
            password="password123",
            confirm_password="password123",
            npm="1234567890"
        )
        assert user.email == "test@example.com"
        assert user.npm == "1234567890"

    def test_user_register_password_mismatch(self):
        """Test that mismatched passwords raise error."""
        with pytest.raises(ValueError):
            UserRegister(
                email="test@example.com",
                name="Test User",
                password="password123",
                confirm_password="different123"
            )

    def test_user_register_invalid_npm(self):
        """Test invalid NPM format."""
        with pytest.raises(ValueError):
            UserRegister(
                email="test@example.com",
                name="Test User",
                password="password123",
                confirm_password="password123",
                npm="12345"  # Too short
            )

class TestAuthService:
    """Test authentication service."""

    @pytest.mark.asyncio
    async def test_register_user(self, db: AsyncIOMotorDatabase):
        """Test user registration."""
        service = AuthService(db)
        user_data = UserRegister(
            email="newuser@example.com",
            name="New User",
            password="password123",
            confirm_password="password123",
            npm="9876543210"
        )

        user = await service.register_user(user_data)
        assert user["email"] == "newuser@example.com"
        assert user["role"] == "mahasiswa"
        assert "password_hash" in user

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, db: AsyncIOMotorDatabase):
        """Test that duplicate email raises error."""
        service = AuthService(db)
        user_data = UserRegister(
            email="duplicate@example.com",
            name="User One",
            password="password123",
            confirm_password="password123"
        )

        await service.register_user(user_data)

        with pytest.raises(ValueError, match="Email sudah terdaftar"):
            await service.register_user(user_data)

    @pytest.mark.asyncio
    async def test_login_success(self, db: AsyncIOMotorDatabase):
        """Test successful login."""
        service = AuthService(db)

        # Register first
        user_data = UserRegister(
            email="login@example.com",
            name="Login User",
            password="password123",
            confirm_password="password123"
        )
        await service.register_user(user_data)

        # Login
        credentials = UserLogin(email="login@example.com", password="password123")
        user = await service.login_user(credentials)

        assert user is not None
        assert user["email"] == "login@example.com"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, db: AsyncIOMotorDatabase):
        """Test login with wrong password."""
        service = AuthService(db)

        # Register first
        user_data = UserRegister(
            email="wrongpass@example.com",
            name="Wrong Pass User",
            password="password123",
            confirm_password="password123"
        )
        await service.register_user(user_data)

        # Login with wrong password
        credentials = UserLogin(email="wrongpass@example.com", password="wrongpassword")
        user = await service.login_user(credentials)

        assert user is None

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, db: AsyncIOMotorDatabase):
        """Test login with non-existent user."""
        service = AuthService(db)
        credentials = UserLogin(email="nonexistent@example.com", password="password123")
        user = await service.login_user(credentials)

        assert user is None

    @pytest.mark.asyncio
    async def test_create_token(self, db: AsyncIOMotorDatabase):
        """Test JWT token creation."""
        service = AuthService(db)
        user_data = UserRegister(
            email="token@example.com",
            name="Token User",
            password="password123",
            confirm_password="password123"
        )
        user = await service.register_user(user_data)

        token = service.create_user_token(user)
        assert token is not None
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_update_password(self, db: AsyncIOMotorDatabase):
        """Test password update."""
        service = AuthService(db)
        user_data = UserRegister(
            email="updatepass@example.com",
            name="Update Pass User",
            password="oldpassword",
            confirm_password="oldpassword"
        )
        user = await service.register_user(user_data)

        success = await service.update_password(str(user["_id"]), "newpassword123")
        assert success is True

        # Verify new password works
        credentials = UserLogin(email="updatepass@example.com", password="newpassword123")
        logged_in = await service.login_user(credentials)
        assert logged_in is not None
