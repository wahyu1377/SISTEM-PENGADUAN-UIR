"""
Database connection and configuration for MongoDB.
"""
from pymongo import MongoClient, GEOSPHERE
from pymongo.database import Database
from pymongo.errors import CollectionInvalid
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import os

from app.core.config import settings

class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB."""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.db = cls.client[settings.MONGODB_DB_NAME]

        # Create indexes
        await cls.create_indexes()

        print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")

    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB."""
        if cls.client:
            cls.client.close()
            print("Disconnected from MongoDB")

    @classmethod
    async def create_indexes(cls):
        """Create necessary indexes for collections."""
        if cls.db is None:
            return

        # Users collection indexes
        await cls.db.users.create_index("email", unique=True)
        await cls.db.users.create_index("npm", sparse=True)

        # Complaints collection indexes
        await cls.db.complaints.create_index("user_id")
        await cls.db.complaints.create_index("status")
        await cls.db.complaints.create_index("priority")
        await cls.db.complaints.create_index("category")
        await cls.db.complaints.create_index("created_at")
        await cls.db.complaints.create_index([
            ("title", "text"),
            ("description", "text")
        ])

        # Documents collection indexes
        await cls.db.documents.create_index("category")
        await cls.db.documents.create_index("created_at")

        # Attachments collection indexes
        await cls.db.attachments.create_index("complaint_id")
        await cls.db.attachments.create_index("created_at")

        # Vector search index for documents (for RAG)
        try:
            await cls.db.command({
                "createSearchIndex": "documents",
                "name": "vector_index",
                "type": "vectorSearch",
                "fields": [
                    {"path": "embedding", "numDimensions": settings.EMBEDDING_DIMENSIONS, "similarity": "cosine"}
                ]
            })
        except Exception as e:
            print(f"Vector index might already exist: {e}")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls.db

# Dependency for FastAPI
async def get_database() -> AsyncIOMotorDatabase:
    return DatabaseManager.get_db()

# Collections accessor
class Collections:
    users = "users"
    complaints = "complaints"
    documents = "documents"
    attachments = "attachments"
    audit_logs = "audit_logs"
