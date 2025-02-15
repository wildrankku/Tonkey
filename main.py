import os
import asyncio  # ✅ Import added
from datetime import datetime, UTC, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from handlers import *
from admin_handlers import *
from database import db
from utils import *
from dotenv import load_dotenv

load_dotenv()

# ------------------- Message Tracking -------------------
async def track_activity(update: Update, context: CallbackContext):
    if not update.message or update.message.chat.type not in ["group", "supergroup"]:
        return
    
    user = update.message.from_user
    chat = update.message.chat
    now = datetime.now(UTC)
    
    # Update group info
    await db.track_group(chat.id, await clean_name(chat.title))
    
    # Update counts
    await db.daily_stats.update_one(
        {"user_id": user.id, "group_id": chat.id, "date": now.replace(hour=0, minute=0, second=0, microsecond=0)},
        {"$inc": {"count": 1}},
        upsert=True
    )
    await db.overall_stats.update_one(
        {"user_id": user.id, "group_id": chat.id},
        {"$inc": {"count": 1}},
        upsert=True
    )
    await update_global_user(user.id, user.first_name)

# ------------------- Setup Handlers -------------------
def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gstat", gstat))
    app.add_handler(CommandHandler("topgroups", top_groups))
    app.add_handler(CommandHandler("topusers", top_users))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("stats", bot_stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("addsudo", add_sudo))
    app.add_handler(CommandHandler("sudolist", sudolist))
    app.add_handler(MessageHandler(filters.ALL, track_activity))
    app.add_handler(CallbackQueryHandler(button_handler))

# ------------------- Main (Async Fix) -------------------
async def main():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    setup_handlers(app)
    
    # Scheduled Jobs
    job_queue = app.job_queue
    job_queue.run_daily(daily_reset, time=datetime.time(0, 0, tzinfo=datetime.timezone.utc))
    
    await app.initialize()
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())  # ✅ Correct async entry point
