import re
import asyncio  # ✅ Import added
from telegram import Update
from database import db
from datetime import datetime, UTC  # ✅ Correct UTC import

async def escape_markdown(text: str) -> str:
    return re.sub(r"([_*\[\]()~`>#+=|{}.!-])", r"\\\1", text)

async def get_uptime() -> str:
    record = await db.bot_analytics.find_one({"_id": "uptime"})
    start_time = record["start_time"]
    delta = datetime.now(UTC) - start_time  # ✅ datetime.UTC fixed
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes = rem // 60
    return f"{days}d {hours}h {minutes}m"

async def is_sudo(user_id: int) -> bool:
    sudo = await db.sudo_users.find_one({"user_id": user_id})
    return bool(sudo)

async def update_global_user(user_id: int, username: str, count: int = 1):
    await db.global_users.update_one(
        {"user_id": user_id},
        {"$inc": {"total": count}, "$set": {"username": username}},
        upsert=True
    )
