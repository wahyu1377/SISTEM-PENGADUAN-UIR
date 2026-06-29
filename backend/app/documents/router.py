"""
Documents API routes for knowledge base management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
import io
import pdfplumber
import docx

from app.core.database import get_database
from app.core.security import get_current_admin
from app.core.config import settings
from app.documents.schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentUploadResponse,
    DocumentCategory
)
from app.documents.service import DocumentService

router = APIRouter(prefix="/api/admin/documents", tags=["Documents (Admin)"])

def get_document_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> DocumentService:
    return DocumentService(db)

def document_to_response(doc: dict) -> DocumentResponse:
    """Convert document to response schema."""
    return DocumentResponse(
        id=str(doc["_id"]),
        title=doc.get("title", ""),
        content=doc.get("content", ""),
        category=doc.get("category", ""),
        source=doc.get("source"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        chunk_count=doc.get("chunk_count")
    )

# SPECIFIC ROUTES MUST COME BEFORE PARAMETERIZED ROUTES

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    admin_user: dict = Depends(get_current_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Create a new document in knowledge base (admin only)."""
    document = await service.create_document(document_data)
    return document_to_response(document)

@router.get("", response_model=DocumentListResponse)
async def get_all_documents(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    category: Optional[DocumentCategory] = None,
    admin_user: dict = Depends(get_current_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Get all documents (admin only)."""
    documents, total = await service.get_all_documents(
        page=page,
        per_page=per_page,
        category=category
    )

    return DocumentListResponse(
        total=total,
        page=page,
        per_page=per_page,
        documents=[document_to_response(d) for d in documents]
    )

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: DocumentCategory = Form(...),
    admin_user: dict = Depends(get_current_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Upload and process document file (admin only)."""
    # Validate file extension
    ext = "." + file.filename.split(".")[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipe file tidak diizinkan. Gunakan: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ukuran file terlalu besar (maksimal 10MB)"
        )

    # Extract text based on file type
    try:
        if ext == ".pdf":
            text = extract_pdf_text(content)
        elif ext == ".docx":
            text = extract_docx_text(content)
        elif ext == ".txt":
            text = content.decode("utf-8")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format file tidak didukung"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gagal memproses file: {str(e)}"
        )

    # Process and save document
    result = await service.upload_and_process_file(
        filename=file.filename,
        content=text,
        category=category
    )

    return DocumentUploadResponse(
        message="Dokumen berhasil diupload dan diproses",
        document_id=result["document_id"],
        chunks_created=result["chunks_created"]
    )

@router.get("/search/relevant")
async def search_relevant_documents(
    query: str = Query(..., min_length=3),
    limit: int = Query(5, ge=1, le=10),
    admin_user: dict = Depends(get_current_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Search relevant documents for RAG (admin only)."""
    results = await service.search_documents(query, limit)
    return {"results": results}

@router.get("/statistics/summary")
async def get_document_statistics(
    admin_user: dict = Depends(get_current_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Get document statistics (admin only)."""
    stats = await service.get_statistics()
    return stats

# PARAMETERIZED ROUTES COME AFTER SPECIFIC ROUTES

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    admin_user: dict = Depends(get_current_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Get document by ID (admin only)."""
    document = await service.get_document_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dokumen tidak ditemukan"
        )

    return document_to_response(document)

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    admin_user: dict = Depends(get_current_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Update document (admin only)."""
    document = await service.update_document(document_id, update_data)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dokumen tidak ditemukan"
        )

    return document_to_response(document)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    admin_user: dict = Depends(get_current_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Delete document (admin only)."""
    deleted = await service.delete_document(document_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dokumen tidak ditemukan"
        )

# Helper functions for file extraction
def extract_pdf_text(content: bytes) -> str:
    """Extract text from PDF file."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)

def extract_docx_text(content: bytes) -> str:
    """Extract text from DOCX file."""
    doc = docx.Document(io.BytesIO(content))
    text_parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)
    return "\n\n".join(text_parts)
