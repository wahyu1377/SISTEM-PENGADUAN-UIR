"""
Core module initialization.
"""
from app.core.config import settings
from app.core.database import DatabaseManager, get_database, Collections
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    get_current_user,
    get_current_admin,
    TokenData
)

__all__ = [
    "settings",
    "DatabaseManager",
    "get_database",
    "Collections",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_token",
    "get_current_user",
    "get_current_admin",
    "TokenData"
]
