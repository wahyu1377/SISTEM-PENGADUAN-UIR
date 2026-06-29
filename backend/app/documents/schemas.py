"""
Documents schemas for knowledge base management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentCategory(str, Enum):
    SOP = "sop"
    STRUKTUR_ORGANISASI = "struktur_organisasi"
    PANDUAN_LAYANAN = "panduan_layanan"
    LAINNYA = "lainnya"

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    category: DocumentCategory
    source: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    category: Optional[DocumentCategory] = None
    source: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    source: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    chunk_count: Optional[int] = None

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    documents: List[DocumentResponse]

class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str
    chunks_created: int
