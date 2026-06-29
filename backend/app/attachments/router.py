"""
Attachments API routes.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.core.database import get_database
from app.core.security import get_current_user, get_current_admin
from app.attachments.service import AttachmentService
from app.attachments.schemas import AttachmentResponse, AttachmentListResponse

router = APIRouter(prefix="/api/attachments", tags=["Attachments"])

def get_attachment_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> AttachmentService:
    return AttachmentService(db)


@router.post("/complaint/{complaint_id}", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    complaint_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    service: AttachmentService = Depends(get_attachment_service)
):
    """Upload an attachment for a complaint."""
    try:
        content = await file.read()
        attachment = await service.upload_attachment(
            complaint_id=complaint_id,
            file_content=content,
            filename=file.filename,
            content_type=file.content_type
        )

        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal mengupload lampiran"
            )

        # Build URL for the attachment
        attachment_id = str(attachment["_id"])
        attachment["url"] = f"/api/attachments/{attachment_id}/file"

        return AttachmentResponse(
            id=attachment_id,
            complaint_id=attachment["complaint_id"],
            filename=attachment["filename"],
            original_filename=attachment["original_filename"],
            file_type=attachment["file_type"],
            file_size=attachment["file_size"],
            url=attachment["url"],
            created_at=attachment["created_at"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/complaint/{complaint_id}", response_model=AttachmentListResponse)
async def get_complaint_attachments(
    complaint_id: str,
    current_user: dict = Depends(get_current_user),
    service: AttachmentService = Depends(get_attachment_service)
):
    """Get all attachments for a complaint."""
    attachments = await service.get_attachments(complaint_id)

    response_list = []
    for att in attachments:
        att_id = str(att["_id"])
        response_list.append(AttachmentResponse(
            id=att_id,
            complaint_id=att["complaint_id"],
            filename=att["filename"],
            original_filename=att["original_filename"],
            file_type=att["file_type"],
            file_size=att["file_size"],
            url=f"/api/attachments/{att_id}/file",
            created_at=att["created_at"]
        ))

    return AttachmentListResponse(
        attachments=response_list,
        total=len(response_list)
    )


@router.get("/{attachment_id}/file")
async def download_attachment(
    attachment_id: str,
    current_user: dict = Depends(get_current_user),
    service: AttachmentService = Depends(get_attachment_service)
):
    """Download an attachment file."""
    attachment = await service.get_attachment(attachment_id)

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lampiran tidak ditemukan"
        )

    file_path = attachment.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File tidak ditemukan"
        )

    return FileResponse(
        path=file_path,
        filename=attachment["original_filename"],
        media_type=attachment["file_type"]
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: str,
    current_user: dict = Depends(get_current_user),
    service: AttachmentService = Depends(get_attachment_service)
):
    """Delete an attachment."""
    deleted = await service.delete_attachment(attachment_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lampiran tidak ditemukan"
        )
