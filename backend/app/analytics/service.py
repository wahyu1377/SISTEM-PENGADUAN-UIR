"""
Analytics service for dashboard statistics.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import Collections
from app.analytics.schemas import (
    OverviewStats,
    StatusDistribution,
    PriorityDistribution,
    CategoryDistribution,
    TrendData,
    UnitPerformance,
    OverviewResponse,
    TrendsResponse,
    CategoriesResponse,
    UnitPerformanceResponse
)

class AnalyticsService:
    """Service for generating analytics and statistics."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[Collections.complaints]

    async def get_overview_stats(self) -> OverviewStats:
        """Get overview statistics."""
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        # Total complaints
        total = await self.collection.count_documents({})

        # Status counts
        status_counts = {}
        for status in ["pending", "analyzing", "reviewed", "forwarded", "resolved", "rejected"]:
            count = await self.collection.count_documents({"status": status})
            status_counts[status] = count

        # This month
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        complaints_this_month = await self.collection.count_documents({
            "created_at": {"$gte": this_month_start}
        })

        # Last month
        last_month_end = this_month_start
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        complaints_last_month = await self.collection.count_documents({
            "created_at": {"$gte": last_month_start, "$lt": last_month_end}
        })

        # Calculate growth
        growth = None
        if complaints_last_month > 0:
            growth = ((complaints_this_month - complaints_last_month) / complaints_last_month) * 100

        # Average resolution time
        avg_resolution = await self._calculate_avg_resolution_time()

        return OverviewStats(
            total_complaints=total,
            pending_complaints=status_counts.get("pending", 0) + status_counts.get("analyzing", 0),
            resolved_complaints=status_counts.get("resolved", 0),
            average_resolution_hours=avg_resolution,
            complaints_this_month=complaints_this_month,
            complaints_last_month=complaints_last_month,
            growth_percentage=growth
        )

    async def get_status_distribution(self) -> List[StatusDistribution]:
        """Get distribution of complaints by status."""
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]

        total = await self.collection.count_documents({})
        results = []

        async for stat in self.collection.aggregate(pipeline):
            results.append(StatusDistribution(
                status=stat["_id"],
                count=stat["count"],
                percentage=(stat["count"] / total * 100) if total > 0 else 0
            ))

        return sorted(results, key=lambda x: x.count, reverse=True)

    async def get_priority_distribution(self) -> List[PriorityDistribution]:
        """Get distribution of complaints by priority."""
        pipeline = [
            {"$match": {"priority": {"$ne": None}}},
            {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
        ]

        total_with_priority = await self.collection.count_documents({"priority": {"$ne": None}})
        results = []

        async for stat in self.collection.aggregate(pipeline):
            results.append(PriorityDistribution(
                priority=stat["_id"],
                count=stat["count"],
                percentage=(stat["count"] / total_with_priority * 100) if total_with_priority > 0 else 0
            ))

        return sorted(results, key=lambda x: x.count, reverse=True)

    async def get_category_distribution(self) -> List[CategoryDistribution]:
        """Get distribution of complaints by category."""
        pipeline = [
            {"$match": {"category": {"$ne": None}}},
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "total_resolution": {
                        "$sum": {
                            "$cond": [
                                {"$and": [{"$ne": ["$resolved_at", None]}, {"$ne": ["$created_at", None]}]},
                                {"$divide": [{"$subtract": ["$resolved_at", "$created_at"]}, 3600000]},
                                0
                            ]
                        }
                    },
                    "resolved_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "resolved"]}, 1, 0]}
                    }
                }
            }
        ]

        results = []

        async for stat in self.collection.aggregate(pipeline):
            avg_hours = None
            if stat["resolved_count"] > 0:
                avg_hours = stat["total_resolution"] / stat["resolved_count"]

            results.append(CategoryDistribution(
                category=stat["_id"],
                count=stat["count"],
                percentage=0,  # Will be calculated later
                avg_resolution_hours=avg_hours
            ))

        total = sum(c.count for c in results)
        for r in results:
            r.percentage = (r.count / total * 100) if total > 0 else 0

        return sorted(results, key=lambda x: x.count, reverse=True)

    async def get_trends(self, days: int = 30) -> List[TrendData]:
        """Get complaint trends over time."""
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)

        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                    },
                    "count": {"$sum": 1},
                    "resolved": {
                        "$sum": {"$cond": [{"$eq": ["$status", "resolved"]}, 1, 0]}
                    }
                }
            },
            {"$sort": {"_id": 1}}
        ]

        results = []
        async for stat in self.collection.aggregate(pipeline):
            results.append(TrendData(
                date=stat["_id"],
                count=stat["count"],
                resolved=stat.get("resolved", 0)
            ))

        return results

    async def get_unit_performance(self) -> List[UnitPerformance]:
        """Get performance metrics by assigned unit."""
        pipeline = [
            {"$match": {"assigned_unit": {"$ne": None}}},
            {
                "$group": {
                    "_id": "$assigned_unit",
                    "assigned_count": {"$sum": 1},
                    "resolved_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "resolved"]}, 1, 0]}
                    },
                    "total_resolution": {
                        "$sum": {
                            "$cond": [
                                {"$and": [{"$ne": ["$resolved_at", None]}, {"$ne": ["$created_at", None]}]},
                                {"$divide": [{"$subtract": ["$resolved_at", "$created_at"]}, 3600000]},
                                0
                            ]
                        }
                    }
                }
            }
        ]

        results = []
        async for stat in self.collection.aggregate(pipeline):
            avg_hours = None
            if stat["resolved_count"] > 0:
                avg_hours = stat["total_resolution"] / stat["resolved_count"]

            results.append(UnitPerformance(
                unit=stat["_id"],
                assigned_count=stat["assigned_count"],
                resolved_count=stat["resolved_count"],
                avg_resolution_hours=avg_hours
            ))

        return sorted(results, key=lambda x: x.assigned_count, reverse=True)

    async def _calculate_avg_resolution_time(self) -> float:
        """Calculate average resolution time in hours."""
        pipeline = [
            {
                "$match": {
                    "status": "resolved",
                    "resolved_at": {"$ne": None},
                    "created_at": {"$ne": None}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_hours": {
                        "$sum": {
                            "$divide": [
                                {"$subtract": ["$resolved_at", "$created_at"]},
                                3600000  # Convert to hours
                            ]
                        }
                    },
                    "count": {"$sum": 1}
                }
            }
        ]

        async for result in self.collection.aggregate(pipeline):
            if result["count"] > 0:
                return round(result["total_hours"] / result["count"], 2)

        return None

    async def get_full_analytics(self) -> Dict[str, Any]:
        """Get complete analytics data."""
        overview_stats = await self.get_overview_stats()
        status_dist = await self.get_status_distribution()
        priority_dist = await self.get_priority_distribution()
        category_dist = await self.get_category_distribution()
        trends = await self.get_trends()
        unit_perf = await self.get_unit_performance()

        return {
            "overview": OverviewResponse(
                stats=overview_stats,
                status_distribution=status_dist,
                priority_distribution=priority_dist
            ),
            "trends": TrendsResponse(
                trends=trends,
                total_period=len(trends)
            ),
            "categories": CategoriesResponse(
                categories=category_dist,
                total=sum(c.count for c in category_dist)
            ),
            "unit_performance": UnitPerformanceResponse(units=unit_perf)
        }
