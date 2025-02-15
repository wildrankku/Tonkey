import os
import asyncio
from datetime import datetime, UTC
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.uri = os.getenv("MONGO_URI")
        if not self.uri:
            raise ValueError("❌ MONGO_URI environment variable not set!")
            
        self.client = AsyncIOMotorClient(
            self.uri,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=20000
        )
        self.db = self.client.get_database()
        asyncio.run(self._initialize())
        self._initialized = True

    async def _initialize(self):
        try:
            await self.client.admin.command('ping')
            print("✅ MongoDB Connected!")
            
            # Initialize collections
            self.daily_stats = self.db.daily
            self.overall_stats = self.db.overall
            self.groups = self.db.groups
            self.global_users = self.db.global_users
            self.sudo_users = self.db.sudo_users
            self.bot_analytics = self.db.bot_analytics
            
            # Create uptime record
            if not await self.bot_analytics.find_one({"_id": "uptime"}):
                await self.bot_analytics.insert_one({
                    "_id": "uptime",
                    "start_time": datetime.now(UTC)
                })
                
        except ServerSelectionTimeoutError as e:
            print(f"❌ Connection Failed: {str(e)}")
            raise

# Singleton instance
db = Database()
