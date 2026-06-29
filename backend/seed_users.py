"""
Seed Script - Create initial users for production deployment
Run this script ONCE after deploying to production to create default accounts.
"""
import asyncio
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB Connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "uir_complaints")

# Default users to create
DEFAULT_USERS = [
    {
        "email": "admin@uir.ac.id",
        "name": "Administrator",
        "password": "admin123456",
        "role": "admin",
        "npm": None
    },
    {
        "email": "test@uir.ac.id",
        "name": "Test User",
        "password": "test123456",
        "role": "mahasiswa",
        "npm": "2109010001"
    },
    {
        "email": "mahasiswa1@uir.ac.id",
        "name": "Mahasiswa Satu",
        "password": "password123",
        "role": "mahasiswa",
        "npm": "2109010002"
    },
    {
        "email": "andimahasiswa@uir.ac.id",
        "name": "Andi Mahasiswa",
        "password": "test123456",
        "role": "mahasiswa",
        "npm": "2109010003"
    },
    {
        "email": "student2024@uir.ac.id",
        "name": "Student 2024",
        "password": "test123456",
        "role": "mahasiswa",
        "npm": "2409010001"
    }
]

async def create_users():
    """Create default users in MongoDB."""
    print("🚀 Starting user seed script...")
    print(f"📦 Connecting to MongoDB: {MONGODB_URL}")
    print(f"📁 Database: {MONGODB_DB_NAME}")
    print()

    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]
    users_collection = db.users

    # Create indexes
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("npm", sparse=True)
    print("✅ Database indexes created")

    created_count = 0
    skipped_count = 0

    for user_data in DEFAULT_USERS:
        email = user_data["email"]
        name = user_data["name"]
        password = user_data["password"]
        role = user_data["role"]
        npm = user_data["npm"]

        # Check if user already exists
        existing_user = await users_collection.find_one({"email": email})

        if existing_user:
            print(f"⏭️  Skipping (already exists): {email}")
            skipped_count += 1
            continue

        # Hash password
        password_hash = pwd_context.hash(password)

        # Create user document
        user_doc = {
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "role": role,
            "npm": npm,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Insert user
        result = await users_collection.insert_one(user_doc)
        print(f"✅ Created: {email} ({role}) - NPM: {npm or 'N/A'}")
        created_count += 1

    print()
    print("=" * 50)
    print("📊 SEED SUMMARY")
    print("=" * 50)
    print(f"✅ Created: {created_count} users")
    print(f"⏭️  Skipped: {skipped_count} users (already exist)")
    print(f"📝 Total: {len(DEFAULT_USERS)} users")
    print()

    if created_count > 0:
        print("📋 LOGIN CREDENTIALS:")
        print("-" * 50)
        for user_data in DEFAULT_USERS:
            if user_data["email"] in [u["email"] for u in DEFAULT_USERS[:created_count]]:
                print(f"  Email: {user_data['email']}")
                print(f"  Password: {user_data['password']}")
                print(f"  Role: {user_data['role']}")
                print()
    else:
        print("✅ All users already exist!")

    # Close connection
    client.close()
    print("🔌 MongoDB connection closed")
    print("🎉 Seed script completed!")

async def delete_all_users():
    """Delete all users (for testing)."""
    print("⚠️  Deleting all users...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]
    users_collection = db.users

    result = await users_collection.delete_many({})
    print(f"✅ Deleted {result.deleted_count} users")

    client.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed users for UIR Complaints System")
    parser.add_argument("--delete", action="store_true", help="Delete all users instead of creating")
    args = parser.parse_args()

    if args.delete:
        asyncio.run(delete_all_users())
    else:
        asyncio.run(create_users())
