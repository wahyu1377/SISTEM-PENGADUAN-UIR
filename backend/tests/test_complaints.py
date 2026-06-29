"""
Tests for complaints module.
"""
import pytest
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.complaints.service import ComplaintService
from app.complaints.schemas import ComplaintCreate, ComplaintUpdate, ComplaintStatusUpdate, ComplaintStatus
from app.auth.service import AuthService
from app.auth.schemas import UserRegister

class TestComplaintSchemas:
    """Test complaint schemas."""

    def test_complaint_create_valid(self):
        """Test valid complaint creation."""
        complaint = ComplaintCreate(
            title="AC Ruang Kelas Rusak",
            description="AC di Ruang B203 tidak berfungsi sejak 3 hari lalu"
        )
        assert complaint.title == "AC Ruang Kelas Rusak"
        assert len(complaint.description) > 20

    def test_complaint_create_title_too_short(self):
        """Test that short title raises error."""
        with pytest.raises(ValueError):
            ComplaintCreate(
                title="AC",  # Too short
                description="AC tidak berfungsi"
            )

    def test_complaint_create_description_too_short(self):
        """Test that short description raises error."""
        with pytest.raises(ValueError):
            ComplaintCreate(
                title="AC Rusak",
                description="AC tidak berfungsi"  # Too short (needs 20 chars)
            )

    def test_status_update_valid(self):
        """Test valid status update."""
        update = ComplaintStatusUpdate(status=ComplaintStatus.RESOLVED)
        assert update.status == ComplaintStatus.RESOLVED

class TestComplaintService:
    """Test complaint service."""

    @pytest.mark.asyncio
    async def test_create_complaint(self, db: AsyncIOMotorDatabase):
        """Test complaint creation."""
        # Create user first
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="student@example.com",
            name="Student User",
            password="password123",
            confirm_password="password123",
            npm="1111111111"
        )
        user = await auth_service.register_user(user_data)

        # Create complaint
        service = ComplaintService(db)
        complaint_data = ComplaintCreate(
            title="WiFi Kampus Lambat",
            description="Koneksi WiFi di area perpustakaan sangat lambat dan sering terputus-putus"
        )

        complaint = await service.create_complaint(str(user["_id"]), complaint_data)

        assert complaint["user_id"] == str(user["_id"])
        assert complaint["title"] == "WiFi Kampus Lambat"
        assert complaint["status"] in ["pending", "analyzing"]

    @pytest.mark.asyncio
    async def test_get_user_complaints(self, db: AsyncIOMotorDatabase):
        """Test getting user complaints."""
        # Create user
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="list@example.com",
            name="List User",
            password="password123",
            confirm_password="password123",
            npm="2222222222"
        )
        user = await auth_service.register_user(user_data)

        # Create multiple complaints
        service = ComplaintService(db)
        for i in range(3):
            complaint_data = ComplaintCreate(
                title=f"Complaint {i+1}",
                description=f"Description for complaint number {i+1} that is longer than 20 characters"
            )
            await service.create_complaint(str(user["_id"]), complaint_data)

        # Get complaints
        complaints, total = await service.get_user_complaints(str(user["_id"]))

        assert total == 3
        assert len(complaints) == 3

    @pytest.mark.asyncio
    async def test_get_complaint_by_id(self, db: AsyncIOMotorDatabase):
        """Test getting complaint by ID."""
        # Create user
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="getbyid@example.com",
            name="Get By ID User",
            password="password123",
            confirm_password="password123",
            npm="3333333333"
        )
        user = await auth_service.register_user(user_data)

        # Create complaint
        service = ComplaintService(db)
        complaint_data = ComplaintCreate(
            title="Get By ID Test",
            description="Testing get complaint by ID functionality properly"
        )
        created = await service.create_complaint(str(user["_id"]), complaint_data)

        # Get by ID
        retrieved = await service.get_complaint_by_id(str(created["_id"]))

        assert retrieved is not None
        assert str(retrieved["_id"]) == str(created["_id"])

    @pytest.mark.asyncio
    async def test_update_complaint_status(self, db: AsyncIOMotorDatabase):
        """Test updating complaint status."""
        # Create user
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="status@example.com",
            name="Status User",
            password="password123",
            confirm_password="password123",
            npm="4444444444"
        )
        user = await auth_service.register_user(user_data)

        # Create complaint
        service = ComplaintService(db)
        complaint_data = ComplaintCreate(
            title="Status Update Test",
            description="Testing status update functionality correctly works"
        )
        created = await service.create_complaint(str(user["_id"]), complaint_data)

        # Update status
        status_update = ComplaintStatusUpdate(status=ComplaintStatus.RESOLVED)
        updated = await service.update_complaint_status(
            str(created["_id"]),
            status_update,
            is_admin=True
        )

        assert updated is not None
        assert updated["status"] == ComplaintStatus.RESOLVED.value
        assert updated["resolved_at"] is not None

    @pytest.mark.asyncio
    async def test_delete_complaint(self, db: AsyncIOMotorDatabase):
        """Test deleting a complaint."""
        # Create user
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="delete@example.com",
            name="Delete User",
            password="password123",
            confirm_password="password123",
            npm="5555555555"
        )
        user = await auth_service.register_user(user_data)

        # Create complaint
        service = ComplaintService(db)
        complaint_data = ComplaintCreate(
            title="Delete Test",
            description="Testing delete functionality for complaints properly"
        )
        created = await service.create_complaint(str(user["_id"]), complaint_data)

        # Delete
        deleted = await service.delete_complaint(str(created["_id"]), is_admin=True)
        assert deleted is True

        # Verify deleted
        retrieved = await service.get_complaint_by_id(str(created["_id"]))
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_non_admin_cannot_delete(self, db: AsyncIOMotorDatabase):
        """Test that non-admin cannot delete complaints."""
        # Create user
        auth_service = AuthService(db)
        user_data = UserRegister(
            email="nondelete@example.com",
            name="No Delete User",
            password="password123",
            confirm_password="password123",
            npm="6666666666"
        )
        user = await auth_service.register_user(user_data)

        # Create complaint
        service = ComplaintService(db)
        complaint_data = ComplaintCreate(
            title="No Delete Test",
            description="Testing that non-admin cannot delete complaints"
        )
        created = await service.create_complaint(str(user["_id"]), complaint_data)

        # Try to delete as non-admin
        with pytest.raises(PermissionError):
            await service.delete_complaint(str(created["_id"]), is_admin=False)
