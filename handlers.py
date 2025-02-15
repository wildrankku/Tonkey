import asyncio
import datetime
from datetime import UTC
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import db
from utils import *
import re

# ------------------- /start Handler -------------------
async def start(update: Update, context: CallbackContext):
    try:
        user = update.effective_user
        keyboard = [
            [InlineKeyboardButton("➕ Add me in your group", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings"), 
             InlineKeyboardButton("🔄 Update", url="https://t.me/samurais_network")],
            [InlineKeyboardButton("👑 Owner", url="https://t.me/Itz_Marv1n"), 
             InlineKeyboardButton("💬 Support", url="https://t.me/anime_group_chat_en")]
        ]
        
        caption = (
            "🌸 *Welcome to Sakura Stats\\!* 🌸\n\n"
            "Konichiwa\\! \\(≧◡≦\\) ♡✨\n"
            "Track messages across all groups\\! 🎀📊\n\n"
            "💬 Compete globally\\!\n"
            "🏆 Daily \\& Overall leaderboards\\!\n"
            "🔄 Auto\\-reset at midnight UTC\\!"
        )

        if update.callback_query:
            await update.callback_query.message.edit_caption(
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="MarkdownV2"
            )
        else:
            await update.message.reply_photo(
                photo="https://telegra.ph/file/28e287f80fd6a7ba67d62.jpg",
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="MarkdownV2"
            )
    except Exception as e:
        print(f"Start Error: {e}")

# ------------------- /gstat Handler -------------------
async def gstat(update: Update, context: CallbackContext):
    try:
        msg = await update.message.reply_photo(
            photo="https://telegra.ph/file/382aff205e8cd367b824c.jpg",
            caption="🌸 Loading Group Leaderboard..."
        )
        await show_leaderboard(context, msg.chat_id, msg.message_id, is_today=True)
    except Exception as e:
        print(f"/gstat Error: {e}")

# ------------------- /topgroups Handler -------------------
async def top_groups(update: Update, context: CallbackContext):
    try:
        msg = await update.message.reply_photo(
            photo="https://telegra.ph/file/group_banner.jpg",
            caption="🌸 Loading Global Groups Leaderboard..."
        )
        await show_group_leaderboard(context, msg.chat_id, msg.message_id, is_today=True)
    except Exception as e:
        print(f"/topgroups Error: {e}")

# ------------------- /topusers Handler -------------------
async def top_users(update: Update, context: CallbackContext):
    try:
        msg = await update.message.reply_photo(
            photo="https://telegra.ph/file/users_banner.jpg",
            caption="🌸 Loading Global Users Leaderboard..."
        )
        await show_global_leaderboard(context, msg.chat_id, msg.message_id, is_today=True)
    except Exception as e:
        print(f"/topusers Error: {e}")

# ------------------- Leaderboard Systems -------------------
async def show_leaderboard(context: CallbackContext, chat_id: int, message_id: int, is_today: bool):
    try:
        collection = db.daily_stats if is_today else db.overall_stats
        date_filter = {"date": datetime.datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)} if is_today else {}
        
        pipeline = [
            {"$match": {"group_id": chat_id, **date_filter}},
            {"$group": {"_id": "$user_id", "count": {"$sum": "$count"}, "name": {"$first": "$first_name"}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        users = await collection.aggregate(pipeline).to_list(length=10)
        total = sum(user.get("count", 0) for user in users)
        
        leaderboard = []
        for idx, user in enumerate(users, 1):
            name = await escape_markdown(user.get("name", "Anonymous"))
            leaderboard.append(f"{idx}\\. {name} \\- {user.get('count', 0):,}")
        
        text = (
            f"🌸 *{'Daily' if is_today else 'Overall'} Leaderboard* 🌸\n\n"
            + "\n".join(leaderboard)
            + f"\n\n📨 Total Messages: {total:,}"
        )
        
        keyboard = [
            [InlineKeyboardButton("📅 Today", callback_data="today"), 
             InlineKeyboardButton("🏆 Overall", callback_data="overall")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        await context.bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        print(f"Leaderboard Error: {e}")

# ------------------- /profile Handler -------------------
async def profile(update: Update, context: CallbackContext):
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        # Current Group Stats
        group_stats = await db.overall_stats.find_one({"user_id": user.id, "group_id": chat.id})
        
        # Global Stats
        global_stats = await db.global_users.find_one({"user_id": user.id})
        total_global = global_stats.get("total", 0) if global_stats else 0
        
        # Global Rank
        rank = await db.global_users.count_documents({"total": {"$gt": total_global}}) + 1
        
        profile_text = (
            f"🌸 *{await escape_markdown(user.first_name)}'s Profile* 🌸\n\n"
            f"📊 *Current Group*\n"
            f"Messages: {group_stats.get('count', 0) if group_stats else 0}\n\n"
            f"🌍 *Global Stats*\n"
            f"Total: {total_global}\n"
            f"Rank: #{rank}"
        )
        
        await update.message.reply_photo(
            photo=user.photo_url if user.photo else "https://telegra.ph/file/default_profile.jpg",
            caption=profile_text,
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        print(f"Profile Error: {e}")

# ------------------- /stats Handler -------------------
async def bot_stats(update: Update, context: CallbackContext):
    try:
        total_groups = await db.groups.count_documents({})
        total_users = await db.global_users.count_documents({})
        uptime = await get_uptime()
        
        stats_text = (
            f"🤖 *Bot Statistics* 🤖\n\n"
            f"• Groups: {total_groups}\n"
            f"• Users: {total_users}\n"
            f"• Uptime: {uptime}"
        )
        
        await update.message.reply_photo(
            photo="https://telegra.ph/file/stats_banner.jpg",
            caption=stats_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]]),
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        print(f"Stats Error: {e}")

# ------------------- Button Handler -------------------
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    async with button_lock:
        try:
            if query.data == "close":
                await query.message.delete()
            elif query.data == "today":
                await show_leaderboard(context, query.message.chat.id, query.message.message_id, is_today=True)
            elif query.data == "overall":
                await show_leaderboard(context, query.message.chat.id, query.message.message_id, is_today=False)
            elif query.data == "refresh_stats":
                await bot_stats(update, context)
            elif query.data == "back":
                await start(update, context)
        except Exception as e:
            print(f"Button Error: {e}")

button_lock = asyncio.Lock()
