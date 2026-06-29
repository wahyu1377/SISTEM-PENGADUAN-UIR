"""
Attachment service for file upload and management.
"""
import os
import uuid
import aiofiles
from datetime import datetime
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import Collections

# Configure upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def ensure_upload_dir():
    """Ensure upload directory exists."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str) -> bool:
    """Check if file type is allowed."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def validate_file_size(size: int) -> bool:
    """Check if file size is within limit."""
    return size <= MAX_FILE_SIZE


class AttachmentService:
    """Service for managing complaint attachments."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[Collections.attachments]

    async def upload_attachment(
        self,
        complaint_id: str,
        file_content: bytes,
        filename: str,
        content_type: str
    ) -> Optional[Dict[str, Any]]:
        """Upload a file attachment."""
        if not is_allowed_file(filename):
            raise ValueError(f"File type not allowed: {get_file_extension(filename)}")

        if not validate_file_size(len(file_content)):
            raise ValueError(f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")

        ensure_upload_dir()

        # Generate unique filename
        ext = get_file_extension(filename)
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        # Create attachment record
        attachment_doc = {
            "complaint_id": complaint_id,
            "filename": unique_filename,
            "original_filename": filename,
            "file_type": content_type,
            "file_size": len(file_content),
            "file_path": file_path,
            "created_at": datetime.utcnow()
        }

        result = await self.collection.insert_one(attachment_doc)
        attachment_doc["_id"] = result.inserted_id

        return attachment_doc

    async def get_attachments(self, complaint_id: str) -> List[Dict[str, Any]]:
        """Get all attachments for a complaint."""
        attachments = []
        async for doc in self.collection.find({"complaint_id": complaint_id}):
            doc["id"] = str(doc["_id"])
            attachments.append(doc)
        return attachments

    async def get_attachment(self, attachment_id: str) -> Optional[Dict[str, Any]]:
        """Get a single attachment by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(attachment_id)})
            if doc:
                doc["id"] = str(doc["_id"])
            return doc
        except:
            return None

    async def delete_attachment(self, attachment_id: str) -> bool:
        """Delete an attachment."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(attachment_id)})
            if not doc:
                return False

            # Delete file from disk
            if os.path.exists(doc.get("file_path", "")):
                os.remove(doc["file_path"])

            # Delete record
            await self.collection.delete_one({"_id": ObjectId(attachment_id)})
            return True
        except:
            return False

    async def count_attachments(self, complaint_id: str) -> int:
        """Count attachments for a complaint."""
        return await self.collection.count_documents({"complaint_id": complaint_id})
