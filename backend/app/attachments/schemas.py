"""
Attachments schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AttachmentResponse(BaseModel):
    id: str
    complaint_id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    url: str
    created_at: datetime

    class Config:
        from_attributes = True

class AttachmentListResponse(BaseModel):
    attachments: list[AttachmentResponse]
    total: int
