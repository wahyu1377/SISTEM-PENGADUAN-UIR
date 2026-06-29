"""
Complaints service for business logic.
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import Collections
from app.complaints.schemas import (
    ComplaintCreate,
    ComplaintUpdate,
    ComplaintStatusUpdate,
    ComplaintStatus,
    ComplaintPriority,
    ComplaintCategory,
    RAGAnalysisResult,
    ComplaintFilter
)
from app.complaints.rag_engine import RAGEngine

class ComplaintService:
    """Service for managing complaints."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[Collections.complaints]
        self.users_collection = db[Collections.users]
        self.rag_engine = RAGEngine(db)

    async def create_complaint(
        self,
        user_id: str,
        complaint_data: ComplaintCreate
    ) -> Dict[str, Any]:
        """Create a new complaint and trigger RAG analysis."""
        now = datetime.utcnow()

        # Initial complaint document
        complaint_doc = {
            "user_id": user_id,
            "title": complaint_data.title,
            "description": complaint_data.description,
            "category": None,
            "priority": None,
            "status": ComplaintStatus.ANALYZING.value,
            "assigned_unit": None,
            "summary": None,
            "reason": None,
            "confidence_score": None,
            "admin_notes": None,
            "created_at": now,
            "updated_at": now,
            "resolved_at": None,
            "analysis_attempts": 0
        }

        result = await self.collection.insert_one(complaint_doc)
        complaint_id = str(result.inserted_id)

        # Trigger RAG analysis asynchronously
        try:
            analysis = await self.rag_engine.analyze_complaint(
                complaint_data.title,
                complaint_data.description
            )

            # Update complaint with analysis results
            await self.collection.update_one(
                {"_id": ObjectId(complaint_id)},
                {
                    "$set": {
                        "category": analysis.category,
                        "priority": analysis.priority,
                        "summary": analysis.summary,
                        "reason": analysis.reason,
                        "confidence_score": analysis.confidence_score,
                        "status": ComplaintStatus.PENDING.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            complaint_doc["category"] = analysis.category
            complaint_doc["priority"] = analysis.priority
            complaint_doc["summary"] = analysis.summary
            complaint_doc["reason"] = analysis.reason
            complaint_doc["confidence_score"] = analysis.confidence_score
            complaint_doc["status"] = ComplaintStatus.PENDING.value

        except Exception as e:
            print(f"RAG Analysis error: {e}")
            # Update status to pending for manual review
            await self.collection.update_one(
                {"_id": ObjectId(complaint_id)},
                {
                    "$set": {
                        "status": ComplaintStatus.PENDING.value,
                        "updated_at": datetime.utcnow()
                    },
                    "$inc": {"analysis_attempts": 1}
                }
            )

        complaint_doc["_id"] = result.inserted_id
        return complaint_doc

    async def get_complaint_by_id(
        self,
        complaint_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get complaint by ID with user access control."""
        try:
            query = {"_id": ObjectId(complaint_id)}

            # Non-admin users can only see their own complaints
            if user_id and not is_admin:
                query["user_id"] = user_id

            complaint = await self.collection.find_one(query)
            return complaint
        except:
            return None

    async def get_user_complaints(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 10,
        filters: Optional[ComplaintFilter] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get paginated complaints for a user."""
        query = {"user_id": user_id}

        if filters:
            if filters.status:
                query["status"] = filters.status.value
            if filters.priority:
                query["priority"] = filters.priority.value
            if filters.category:
                query["category"] = filters.category.value
            if filters.date_from:
                query.setdefault("created_at", {})["$gte"] = filters.date_from
            if filters.date_to:
                query.setdefault("created_at", {})["$lte"] = filters.date_to
            if filters.search:
                query["$or"] = [
                    {"title": {"$regex": filters.search, "$options": "i"}},
                    {"description": {"$regex": filters.search, "$options": "i"}}
                ]

        # Get total count
        total = await self.collection.count_documents(query)

        # Get paginated results
        skip = (page - 1) * per_page
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(per_page)

        complaints = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            complaints.append(doc)

        return complaints, total

    async def get_all_complaints(
        self,
        page: int = 1,
        per_page: int = 10,
        filters: Optional[ComplaintFilter] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all complaints (admin only)."""
        query = {}

        if filters:
            if filters.status:
                query["status"] = filters.status.value
            if filters.priority:
                query["priority"] = filters.priority.value
            if filters.category:
                query["category"] = filters.category.value
            if filters.date_from:
                query.setdefault("created_at", {})["$gte"] = filters.date_from
            if filters.date_to:
                query.setdefault("created_at", {})["$lte"] = filters.date_to
            if filters.search:
                query["$text"] = {"$search": filters.search}

        total = await self.collection.count_documents(query)

        skip = (page - 1) * per_page
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(per_page)

        complaints = []
        async for doc in cursor:
            # Enrich with user info
            user = await self.users_collection.find_one({"_id": ObjectId(doc["user_id"])})
            doc["user_name"] = user.get("name", "Unknown") if user else "Unknown"
            doc["user_npm"] = user.get("npm") if user else None
            doc["_id"] = str(doc["_id"])
            complaints.append(doc)

        return complaints, total

    async def update_complaint(
        self,
        complaint_id: str,
        update_data: ComplaintUpdate,
        is_admin: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Update complaint details."""
        if not is_admin:
            raise PermissionError("Only admin can update complaints")

        try:
            update_dict = {k: v.value if hasattr(v, 'value') else v
                          for k, v in update_data.model_dump().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()

            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(complaint_id)},
                {"$set": update_dict},
                return_document=True
            )

            return result
        except:
            return None

    async def update_complaint_status(
        self,
        complaint_id: str,
        status_update: ComplaintStatusUpdate,
        is_admin: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Update complaint status."""
        if not is_admin:
            raise PermissionError("Only admin can update status")

        try:
            update_dict = {
                "status": status_update.status.value,
                "updated_at": datetime.utcnow()
            }

            if status_update.status == ComplaintStatus.RESOLVED:
                update_dict["resolved_at"] = datetime.utcnow()

            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(complaint_id)},
                {"$set": update_dict},
                return_document=True
            )

            return result
        except:
            return None

    async def delete_complaint(
        self,
        complaint_id: str,
        is_admin: bool = False
    ) -> bool:
        """Delete a complaint (admin only)."""
        if not is_admin:
            raise PermissionError("Only admin can delete complaints")

        try:
            result = await self.collection.delete_one({"_id": ObjectId(complaint_id)})
            return result.deleted_count > 0
        except:
            return False

    async def bulk_update_status(
        self,
        complaint_ids: List[str],
        new_status: ComplaintStatus
    ) -> int:
        """Bulk update status for multiple complaints."""
        try:
            update_dict = {
                "status": new_status.value,
                "updated_at": datetime.utcnow()
            }

            if new_status == ComplaintStatus.RESOLVED:
                update_dict["resolved_at"] = datetime.utcnow()

            result = await self.collection.update_many(
                {"_id": {"$in": [ObjectId(cid) for cid in complaint_ids]}},
                {"$set": update_dict}
            )

            return result.modified_count
        except:
            return 0

    async def re_analyze_complaint(
        self,
        complaint_id: str,
        is_admin: bool = False
    ) -> Optional[RAGAnalysisResult]:
        """Re-run RAG analysis on a complaint."""
        if not is_admin:
            raise PermissionError("Only admin can trigger re-analysis")

        try:
            complaint = await self.collection.find_one({"_id": ObjectId(complaint_id)})
            if not complaint:
                return None

            analysis = await self.rag_engine.analyze_complaint(
                complaint["title"],
                complaint["description"]
            )

            # Update complaint with new analysis
            await self.collection.update_one(
                {"_id": ObjectId(complaint_id)},
                {
                    "$set": {
                        "category": analysis.category,
                        "priority": analysis.priority,
                        "summary": analysis.summary,
                        "reason": analysis.reason,
                        "confidence_score": analysis.confidence_score,
                        "updated_at": datetime.utcnow()
                    },
                    "$inc": {"analysis_attempts": 1}
                }
            )

            return analysis
        except:
            return None
