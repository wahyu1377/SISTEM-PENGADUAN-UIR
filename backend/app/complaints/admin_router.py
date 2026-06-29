"""
Admin Complaints API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
import csv
import io
from datetime import datetime

from app.core.database import get_database
from app.core.security import get_current_admin
from app.complaints.schemas import (
    ComplaintUpdate,
    ComplaintStatusUpdate,
    ComplaintResponse,
    ComplaintListResponse,
    ComplaintFilter,
    BulkStatusUpdate,
    RAGAnalysisResult,
    ComplaintStatus,
    ComplaintPriority,
    ComplaintCategory
)
from app.complaints.service import ComplaintService

router = APIRouter(prefix="/api/admin/complaints", tags=["Admin - Complaints"])

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

# SPECIFIC ROUTES MUST COME BEFORE PARAMETERIZED ROUTES

@router.get("", response_model=ComplaintListResponse)
async def get_all_complaints(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    status_filter: Optional[ComplaintStatus] = None,
    priority: Optional[ComplaintPriority] = None,
    category: Optional[ComplaintCategory] = None,
    search: Optional[str] = None,
    admin_user: dict = Depends(get_current_admin),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Get all complaints (admin only)."""
    filters = ComplaintFilter(
        status=status_filter,
        priority=priority,
        category=category,
        search=search
    )

    complaints, total = await service.get_all_complaints(
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

@router.get("/export")
async def export_complaints_csv(
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    admin_user: dict = Depends(get_current_admin),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Export complaints to CSV (admin only)."""
    filters = ComplaintFilter(
        status=status_filter,
        priority=priority,
        category=category
    )

    complaints, _ = await service.get_all_complaints(
        page=1,
        per_page=10000,
        filters=filters
    )

    def format_datetime(dt):
        if dt:
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        return ''

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'No', 'ID', 'Judul', 'Deskripsi', 'Mahasiswa', 'NPM',
        'Kategori', 'Prioritas', 'Status', 'Unit', 'Catatan Admin',
        'Dibuat', 'Diperbarui', 'Selesai'
    ])

    for idx, complaint in enumerate(complaints, 1):
        writer.writerow([
            idx,
            str(complaint.get('_id', '')),
            complaint.get('title', ''),
            complaint.get('description', ''),
            complaint.get('user_name', ''),
            complaint.get('user_npm', ''),
            complaint.get('category', ''),
            complaint.get('priority', ''),
            complaint.get('status', ''),
            complaint.get('assigned_unit', ''),
            complaint.get('admin_notes', ''),
            format_datetime(complaint.get('created_at')),
            format_datetime(complaint.get('updated_at')),
            format_datetime(complaint.get('resolved_at'))
        ])

    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'laporan_pengaduan_{timestamp}.csv'

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )

@router.post("/bulk-update-status")
async def bulk_update_status(
    bulk_data: BulkStatusUpdate,
    admin_user: dict = Depends(get_current_admin),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Bulk update status for multiple complaints (admin only)."""
    updated = await service.bulk_update_status(
        bulk_data.complaint_ids,
        bulk_data.status
    )

    return {
        "message": f"{updated} pengaduan berhasil diperbarui",
        "updated_count": updated
    }

# PARAMETERIZED ROUTES COME AFTER SPECIFIC ROUTES

@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint_by_id(
    complaint_id: str,
    admin_user: dict = Depends(get_current_admin),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Get complaint detail by ID (admin only)."""
    complaint = await service.get_complaint_by_id(
        complaint_id,
        is_admin=True
    )

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengaduan tidak ditemukan"
        )

    return complaint_to_response(complaint)

@router.put("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: str,
    update_data: ComplaintUpdate,
    admin_user: dict = Depends(get_current_admin),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Update complaint details (admin only)."""
    try:
        complaint = await service.update_complaint(
            complaint_id,
            update_data,
            is_admin=True
        )

        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pengaduan tidak ditemukan"
            )

        return complaint_to_response(complaint)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak"
        )

@router.put("/{complaint_id}/status", response_model=ComplaintResponse)
async def update_complaint_status(
    complaint_id: str,
    status_update: ComplaintStatusUpdate,
    admin_user: dict = Depends(get_current_admin),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Update complaint status (admin only)."""
    try:
        complaint = await service.update_complaint_status(
            complaint_id,
            status_update,
            is_admin=True
        )

        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pengaduan tidak ditemukan"
            )

        return complaint_to_response(complaint)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak"
        )

@router.post("/{complaint_id}/re-analyze", response_model=RAGAnalysisResult)
async def re_analyze_complaint(
    complaint_id: str,
    admin_user: dict = Depends(get_current_admin),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Re-run RAG analysis on a complaint (admin only)."""
    try:
        analysis = await service.re_analyze_complaint(
            complaint_id,
            is_admin=True
        )

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pengaduan tidak ditemukan"
            )

        return analysis
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak"
        )

@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(
    complaint_id: str,
    admin_user: dict = Depends(get_current_admin),
    service: ComplaintService = Depends(get_complaint_service)
):
    """Delete a complaint (admin only)."""
    try:
        deleted = await service.delete_complaint(
            complaint_id,
            is_admin=True
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pengaduan tidak ditemukan"
            )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak"
        )
