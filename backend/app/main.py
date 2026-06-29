"""
Main FastAPI Application
Sistem Pengaduan Mahasiswa Universitas Islam Riau Berbasis RAG
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.database import DatabaseManager
from app.auth.router import router as auth_router
from app.complaints.router import router as complaints_router
from app.complaints.admin_router import router as admin_complaints_router
from app.documents.router import router as documents_router
from app.analytics.router import router as analytics_router
from app.attachments.router import router as attachments_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await DatabaseManager.connect()
    yield
    # Shutdown
    await DatabaseManager.disconnect()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistem Pengaduan Mahasiswa Universitas Islam Riau Berbasis Retrieval-Augmented Generation (RAG)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions."""
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Terjadi kesalahan internal server",
            "error": str(exc) if settings.DEBUG else None
        }
    )

# Include routers
app.include_router(auth_router)
app.include_router(complaints_router)
app.include_router(admin_complaints_router)
app.include_router(documents_router)
app.include_router(analytics_router)
app.include_router(attachments_router)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Selamat datang di Sistem Pengaduan Mahasiswa UIR Berbasis RAG",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
