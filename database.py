import os
import asyncio
from datetime import datetime, UTC
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()

    def _connect(self):
        try:
            # Enhanced connection configuration
            self.client = AsyncIOMotorClient(
                os.getenv("MONGO_URI"),
                serverSelectionTimeoutMS=30000,  # 30 seconds timeout
                connectTimeoutMS=20000,
                socketTimeoutMS=20000,
                retryWrites=True,
                maxPoolSize=100
            )
            self.db = self.client["SakuraStats"]
            asyncio.run(self._initialize_collections())
            asyncio.run(self._test_connection())
        except Exception as e:
            print(f"🔥 Critical DB Error: {e}")
            raise

    async def _test_connection(self):
        try:
            await self.client.admin.command('ping')
            print("✅ MongoDB Connection Successful!")
        except ServerSelectionTimeoutError:
            print("❌ MongoDB Connection Failed: Timeout")
        except Exception as e:
            print(f"❌ MongoDB Connection Failed: {str(e)}")

    async def _initialize_collections(self):
        # Initialize core collections
        self.daily_stats = self.db["daily"]
        self.overall_stats = self.db["overall"]
        self.groups = self.db["groups"]
        self.global_users = self.db["global_users"]
        self.sudo_users = self.db["sudo_users"]
        self.bot_analytics = self.db["bot_analytics"]

        # Initialize uptime record
        if not await self.bot_analytics.find_one({"_id": "uptime"}):
            await self.bot_analytics.insert_one({
                "_id": "uptime",
                "start_time": datetime.now(UTC),
                "last_updated": datetime.now(UTC)
            })

    async def track_group(self, group_id: int, group_name: str):
        """Store group info with automatic retry"""
        try:
            await self.groups.update_one(
                {"_id": group_id},
                {"$set": {
                    "group_name": group_name,
                    "last_active": datetime.now(UTC)
                }},
                upsert=True
            )
        except Exception as e:
            print(f"Group Tracking Error: {e}")

    async def close(self):
        """Graceful shutdown"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB Connection Closed")

# Async context manager for safe initialization
async def get_database():
    db = Database()
    try:
        await db._test_connection()
        return db
    except Exception as e:
        print(f"Database Initialization Failed: {e}")
        raise

db = Database()
