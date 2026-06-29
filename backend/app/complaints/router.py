"""
Complaints API routes - Student endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.core.database import get_database
from app.core.security import get_current_user
from app.complaints.schemas import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintListResponse,
    ComplaintFilter,
    RAGAnalysisResult,
    ComplaintStatus,
    ComplaintPriority
)
from app.complaints.service import ComplaintService

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

def get_complaint_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ComplaintService:
    return ComplaintService(db)

def complaint_to_response(complaint: dict) -> ComplaintResponse:
    """Convert complaint document to response schema."""
    rag_analysis = None
    if complaint.get("category"):
        rag_analysis = RAGAnalysisResult(
            category=complaint.get("category", ""),
            priority=complaint.get("priority", "medium"),
            summary=complaint.get("summary", ""),
            recommended_unit=complaint.get("assigned_unit", ""),
            reason=complaint.get("reason", ""),
            confidence_score=complaint.get("confidence_score", 0.0)
        )

    return ComplaintResponse(
        id=str(complaint["_id"]),
        user_id=complaint.get("user_id", ""),
        user_name=complaint.get("user_name"),
        user_npm=complaint.get("user_npm"),
        title=complaint["title"],
        description=complaint["description"],
        category=complaint.get("category"),
        priority=complaint.get("priority"),
        status=complaint.get("status", "pending"),
        assigned_unit=complaint.get("assigned_unit"),
        summary=complaint.get("summary"),
        reason=complaint.get("reason"),
        confidence_score=complaint.get("confidence_score"),
        rag_analysis=rag_analysis,
        admin_notes=complaint.get("admin_notes"),
        created_at=complaint["created_at"],
        updated_at=complaint["updated_at"],
        resolved_at=complaint.get("resolved_at")
    )

@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    complaint_data: ComplaintCreate,
    current_user: dict = Depends(get_current_user),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Submit a new complaint (mahasiswa only)."""
    complaint = await service.create_complaint(
        str(current_user["_id"]),
        complaint_data
    )
    return complaint_to_response(complaint)

@router.get("", response_model=ComplaintListResponse)
async def get_my_complaints(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    status_filter: Optional[ComplaintStatus] = None,
    priority: Optional[ComplaintPriority] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Get current user's complaints."""
    filters = ComplaintFilter(
        status=status_filter,
        priority=priority,
        search=search
    )

    complaints, total = await service.get_user_complaints(
        str(current_user["_id"]),
        page=page,
        per_page=per_page,
        filters=filters
    )

    return ComplaintListResponse(
        total=total,
        page=page,
        per_page=per_page,
        complaints=[complaint_to_response(c) for c in complaints]
    )

@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint_detail(
    complaint_id: str,
    current_user: dict = Depends(get_current_user),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Get complaint details (own complaints only for mahasiswa)."""
    complaint = await service.get_complaint_by_id(
        complaint_id,
        user_id=str(current_user["_id"]),
        is_admin=current_user["role"] == "admin"
    )

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengaduan tidak ditemukan"
        )

    return complaint_to_response(complaint)