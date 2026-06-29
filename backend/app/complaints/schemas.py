"""
Complaints schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ComplaintStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    REVIEWED = "reviewed"
    FORWARDED = "forwarded"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class ComplaintPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ComplaintCategory(str, Enum):
    AKADEMIK = "Akademik"
    FASILITAS_KAMPUS = "Fasilitas Kampus"
    PERPUSTAKAAN = "Perpustakaan"
    TEKNOLOGI_INFORMASI = "Teknologi Informasi"
    ADMINISTRASI = "Administrasi"
    KEAMANAN_KESELAMATAN = "Keamanan & Keselamatan"
    LAINNYA = "Lainnya"

class ComplaintBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintUpdate(BaseModel):
    category: Optional[ComplaintCategory] = None
    priority: Optional[ComplaintPriority] = None
    assigned_unit: Optional[str] = None
    admin_notes: Optional[str] = None

class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus

class RAGAnalysisResult(BaseModel):
    category: Optional[str] = None
    priority: Optional[str] = "medium"
    summary: Optional[str] = None
    recommended_unit: Optional[str] = "Admin"
    reason: Optional[str] = None
    confidence_score: Optional[float] = 0.5

class ComplaintResponse(ComplaintBase):
    id: str
    user_id: str
    user_name: Optional[str] = None
    user_npm: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: str
    assigned_unit: Optional[str] = None
    summary: Optional[str] = None
    reason: Optional[str] = None
    confidence_score: Optional[float] = None
    rag_analysis: Optional[RAGAnalysisResult] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ComplaintListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    complaints: List[ComplaintResponse]

class ComplaintFilter(BaseModel):
    status: Optional[ComplaintStatus] = None
    priority: Optional[ComplaintPriority] = None
    category: Optional[ComplaintCategory] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None

class BulkStatusUpdate(BaseModel):
    complaint_ids: List[str]
    status: ComplaintStatus
