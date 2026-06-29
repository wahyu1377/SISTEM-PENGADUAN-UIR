"""
Auth module initialization.
"""
from app.auth.router import router as auth_router
from app.auth.service import AuthService
from app.auth.schemas import UserRegister, UserLogin, UserResponse, TokenResponse

__all__ = [
    "auth_router",
    "AuthService",
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse"
]
