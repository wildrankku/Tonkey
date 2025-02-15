import os
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import UTC

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
        self.db = self.client["SakuraStats"]
        
        # Existing Collections
        self.daily_stats = self.db["daily"]
        self.overall_stats = self.db["overall"]
        
        # New Features Collections
        self.groups = self.db["groups"]          # /topgroups के लिए
        self.global_users = self.db["global_users"] # /topusers के लिए
        self.sudo_users = self.db["sudo_users"]    # /sudolist के लिए
        self.bot_analytics = self.db["bot_analytics"] # /stats के लिए
        
        # Initialize Uptime
        asyncio.run(self.init_uptime())
    
    async def init_uptime(self):
        if not await self.bot_analytics.find_one({"_id": "uptime"}):
            await self.bot_analytics.insert_one({
                "_id": "uptime",
                "start_time": datetime.datetime.now(UTC)
            })
    
    async def track_group(self, group_id: int, group_name: str):
        await self.groups.update_one(
            {"_id": group_id},
            {"$set": {"group_name": group_name}},
            upsert=True
        )

db = Database()
