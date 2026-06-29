"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.security import get_current_user
from app.auth.schemas import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    PasswordChange
)
from app.auth.service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> AuthService:
    return AuthService(db)

def user_to_response(user: dict) -> UserResponse:
    """Convert user document to response schema."""
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        role=user["role"],
        npm=user.get("npm"),
        created_at=user["created_at"],
        updated_at=user["updated_at"]
    )

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    service: AuthService = Depends(get_auth_service)
):
    """Register a new student user."""
    try:
        user = await service.register_user(user_data)
        token = service.create_user_token(user)
        return TokenResponse(
            access_token=token,
            user=user_to_response(user)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    service: AuthService = Depends(get_auth_service)
):
    """Login with email and password."""
    user = await service.login_user(credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah"
        )

    token = service.create_user_token(user)
    return TokenResponse(
        access_token=token,
        user=user_to_response(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user)
):
    """Get current authenticated user."""
    return user_to_response(current_user)

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: dict,
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    """Update current user's profile."""
    try:
        updated_user = await service.update_profile(str(current_user["_id"]), profile_data)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal memperbarui profil"
            )

        return user_to_response(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    """Change user password."""
    from app.core.security import verify_password

    if not verify_password(password_data.current_password, current_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password saat ini salah"
        )

    success = await service.update_password(str(current_user["_id"]), password_data.new_password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengubah password"
        )

    return {"message": "Password berhasil diubah"}

@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user)
):
    """Logout current user (client should discard token)."""
    return {"message": "Berhasil logout"}

# Seed endpoint for initial setup (should be disabled in production)
@router.post("/seed", tags=["Setup"])
async def seed_users(
    service: AuthService = Depends(get_auth_service),
    secret_key: str = None
):
    """Seed initial users for the system. Requires secret key."""
    from app.core.config import settings

    # Simple protection - change this or disable in production
    expected_key = "uir-seed-2024"
    if secret_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid secret key"
        )

    # Check if admin already exists
    existing_admin = await service.collection.find_one({"email": "admin@uir.ac.id"})
    if existing_admin:
        return {
            "message": "Users already seeded",
            "users_created": 0
        }

    # Create users
    users_to_create = [
        {"email": "admin@uir.ac.id", "name": "Administrator", "password": "admin123456", "role": "admin"},
        {"email": "test@uir.ac.id", "name": "Test User", "password": "test123456", "role": "mahasiswa", "npm": "2109010001"},
        {"email": "mahasiswa1@uir.ac.id", "name": "Mahasiswa Satu", "password": "password123", "role": "mahasiswa", "npm": "2109010002"},
        {"email": "andimahasiswa@uir.ac.id", "name": "Andi Mahasiswa", "password": "test123456", "role": "mahasiswa", "npm": "2109010003"},
        {"email": "student2024@uir.ac.id", "name": "Student 2024", "password": "test123456", "role": "mahasiswa", "npm": "2409010001"},
    ]

    created = 0
    for user_data in users_to_create:
        try:
            await service.create_admin_user(
                email=user_data["email"],
                name=user_data["name"],
                password=user_data["password"]
            )
            # Update role if mahasiswa
            if user_data["role"] == "mahasiswa":
                await service.collection.update_one(
                    {"email": user_data["email"]},
                    {"$set": {"role": "mahasiswa", "npm": user_data.get("npm")}}
                )
            created += 1
        except Exception as e:
            print(f"Error creating user {user_data['email']}: {e}")

    return {
        "message": f"Successfully created {created} users",
        "users_created": created,
        "credentials": [
            {"email": "admin@uir.ac.id", "password": "admin123456", "role": "admin"},
            {"email": "test@uir.ac.id", "password": "test123456", "role": "mahasiswa"},
            {"email": "mahasiswa1@uir.ac.id", "password": "password123", "role": "mahasiswa"},
            {"email": "andimahasiswa@uir.ac.id", "password": "test123456", "role": "mahasiswa"},
            {"email": "student2024@uir.ac.id", "password": "test123456", "role": "mahasiswa"},
        ]
    }
