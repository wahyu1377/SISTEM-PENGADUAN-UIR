"""
Analytics schemas for dashboard statistics.
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class OverviewStats(BaseModel):
    total_complaints: int
    pending_complaints: int
    resolved_complaints: int
    average_resolution_hours: Optional[float]
    complaints_this_month: int
    complaints_last_month: int
    growth_percentage: Optional[float]

class StatusDistribution(BaseModel):
    status: str
    count: int
    percentage: float

class CategoryDistribution(BaseModel):
    category: str
    count: int
    percentage: float
    avg_resolution_hours: Optional[float]

class PriorityDistribution(BaseModel):
    priority: str
    count: int
    percentage: float

class TrendData(BaseModel):
    date: str
    count: int
    resolved: int

class UnitPerformance(BaseModel):
    unit: str
    assigned_count: int
    resolved_count: int
    avg_resolution_hours: Optional[float]

class OverviewResponse(BaseModel):
    stats: OverviewStats
    status_distribution: List[StatusDistribution]
    priority_distribution: List[PriorityDistribution]

class TrendsResponse(BaseModel):
    trends: List[TrendData]
    total_period: int

class CategoriesResponse(BaseModel):
    categories: List[CategoryDistribution]
    total: int

class UnitPerformanceResponse(BaseModel):
    units: List[UnitPerformance]

class AnalyticsResponse(BaseModel):
    overview: OverviewResponse
    trends: TrendsResponse
    categories: CategoriesResponse
    unit_performance: UnitPerformanceResponse
