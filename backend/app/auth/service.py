"""
Authentication service for user management.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pymongo import ReturnDocument

from app.core.database import Collections
from app.core.security import get_password_hash, verify_password, create_access_token, TokenData
from app.auth.schemas import UserRegister, UserLogin, UserRole

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[Collections.users]

    async def register_user(self, user_data: UserRegister) -> Dict[str, Any]:
        """Register a new user."""
        # Check if email already exists
        existing_user = await self.collection.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("Email sudah terdaftar")

        # Check if NPM already exists (for students)
        if user_data.npm:
            existing_npm = await self.collection.find_one({"npm": user_data.npm})
            if existing_npm:
                raise ValueError("NPM sudah terdaftar")

        # Create user document
        now = datetime.utcnow()
        user_doc = {
            "email": user_data.email,
            "name": user_data.name,
            "password_hash": get_password_hash(user_data.password),
            "npm": user_data.npm,
            "role": UserRole.MAHASISWA.value,
            "created_at": now,
            "updated_at": now,
            "is_active": True
        }

        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        return user_doc

    async def login_user(self, credentials: UserLogin) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data with token."""
        user = await self.collection.find_one({"email": credentials.email})

        if not user:
            return None

        if not verify_password(credentials.password, user["password_hash"]):
            return None

        if not user.get("is_active", True):
            raise ValueError("Akun non-aktif")

        # Update last login
        await self.collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return user

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            return user
        except:
            return None

    async def create_admin_user(
        self,
        email: str,
        name: str,
        password: str
    ) -> Dict[str, Any]:
        """Create an admin user (for initial setup)."""
        existing_user = await self.collection.find_one({"email": email})
        if existing_user:
            raise ValueError("Email sudah terdaftar")

        now = datetime.utcnow()
        user_doc = {
            "email": email,
            "name": name,
            "password_hash": get_password_hash(password),
            "npm": None,
            "role": UserRole.ADMIN.value,
            "created_at": now,
            "updated_at": now,
            "is_active": True
        }

        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        return user_doc

    async def update_password(self, user_id: str, new_password: str) -> bool:
        """Update user password."""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "password_hash": get_password_hash(new_password),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False

    async def update_profile(self, user_id: str, profile_data: dict) -> Optional[Dict[str, Any]]:
        """Update user profile (name, npm)."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            update_fields = {"updated_at": datetime.utcnow()}

            if "name" in profile_data:
                update_fields["name"] = profile_data["name"].strip()

            if "npm" in profile_data:
                npm = profile_data["npm"].strip() if profile_data["npm"] else None
                # Check if npm already exists for another user
                if npm:
                    existing = await self.collection.find_one({
                        "npm": npm,
                        "_id": {"$ne": ObjectId(user_id)}
                    })
                    if existing:
                        raise ValueError("NPM sudah terdaftar")
                update_fields["npm"] = npm

            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields},
                return_document=ReturnDocument.AFTER
            )
            return result
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
            return None

    def create_user_token(self, user: Dict[str, Any]) -> str:
        """Create JWT token for user."""
        token_data = {
            "sub": str(user["_id"]),
            "email": user["email"],
            "role": user["role"]
        }
        return create_access_token(token_data)
