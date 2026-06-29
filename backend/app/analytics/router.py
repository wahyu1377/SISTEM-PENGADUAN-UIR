"""
Analytics API routes for admin dashboard.
"""
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.core.database import get_database
from app.core.security import get_current_admin
from app.analytics.schemas import (
    OverviewResponse,
    TrendsResponse,
    CategoriesResponse,
    UnitPerformanceResponse,
    AnalyticsResponse
)
from app.analytics.service import AnalyticsService

router = APIRouter(prefix="/api/admin/analytics", tags=["Analytics (Admin)"])

def get_analytics_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> AnalyticsService:
    return AnalyticsService(db)

@router.get("/overview", response_model=OverviewResponse)
async def get_overview(
    admin_user: dict = Depends(get_current_admin),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get dashboard overview statistics (admin only)."""
    stats = await service.get_overview_stats()
    status_dist = await service.get_status_distribution()
    priority_dist = await service.get_priority_distribution()

    return OverviewResponse(
        stats=stats,
        status_distribution=status_dist,
        priority_distribution=priority_dist
    )

@router.get("/trends", response_model=TrendsResponse)
async def get_trends(
    days: int = Query(30, ge=7, le=90),
    admin_user: dict = Depends(get_current_admin),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get complaint trends over time (admin only)."""
    trends = await service.get_trends(days)

    return TrendsResponse(
        trends=trends,
        total_period=len(trends)
    )

@router.get("/categories", response_model=CategoriesResponse)
async def get_category_statistics(
    admin_user: dict = Depends(get_current_admin),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get statistics by category (admin only)."""
    categories = await service.get_category_distribution()

    return CategoriesResponse(
        categories=categories,
        total=sum(c.count for c in categories)
    )

@router.get("/units", response_model=UnitPerformanceResponse)
async def get_unit_performance(
    admin_user: dict = Depends(get_current_admin),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get performance by unit (admin only)."""
    units = await service.get_unit_performance()

    return UnitPerformanceResponse(units=units)

@router.get("/full", response_model=AnalyticsResponse)
async def get_full_analytics(
    admin_user: dict = Depends(get_current_admin),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get complete analytics data (admin only)."""
    return await service.get_full_analytics()
