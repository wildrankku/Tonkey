import os
import asyncio
from datetime import datetime, UTC
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

class Database:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI")
        if not self.uri:
            raise ValueError("❌ MONGO_URI environment variable missing!")
        
        # Explicit database name extraction
        if "/?" in self.uri:
            self.db_name = "SakuraStats"  # Default name if not in URI
        else:
            self.db_name = self.uri.split("/")[-1].split("?")[0]
            
        self.client = AsyncIOMotorClient(self.uri)
        self.db = self.client[self.db_name]  # Explicit database selection
        
        asyncio.run(self._verify_connection())

    async def _verify_connection(self):
        try:
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB | Database: {self.db_name}")
            
            # Initialize collections
            self.daily_stats = self.db.daily
            self.overall_stats = self.db.overall
            self.groups = self.db.groups
            self.global_users = self.db.global_users
            self.sudo_users = self.db.sudo_users
            self.bot_analytics = self.db.bot_analytics
            
            # Initialize uptime
            if not await self.bot_analytics.find_one({"_id": "uptime"}):
                await self.bot_analytics.insert_one({
                    "_id": "uptime",
                    "start_time": datetime.now(UTC)
                })
                
        except ServerSelectionTimeoutError as e:
            print(f"❌ Connection Failed: {str(e)}")
            raise

db = Database()
