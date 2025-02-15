import os
import asyncio  # ✅ Import added
from datetime import datetime, UTC  # ✅ Correct UTC import
from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
        self.db = self.client["SakuraStats"]
        
        # Collections
        self.daily_stats = self.db["daily"]
        self.overall_stats = self.db["overall"]
        self.groups = self.db["groups"]
        self.global_users = self.db["global_users"]
        self.sudo_users = self.db["sudo_users"]
        self.bot_analytics = self.db["bot_analytics"]
        
        # Initialize async
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.async_init())  # ✅ Correct async init

    async def async_init(self):  # ✅ Separate async method
        if not await self.bot_analytics.find_one({"_id": "uptime"}):
            await self.bot_analytics.insert_one({
                "_id": "uptime",
                "start_time": datetime.now(UTC)  # ✅ datetime.UTC fixed
            })
    
    async def track_group(self, group_id: int, group_name: str):
        await self.groups.update_one(
            {"_id": group_id},
            {"$set": {"group_name": group_name}},
            upsert=True
        )

db = Database()
