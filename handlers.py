import asyncio
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import db
from utils import *
from datetime import UTC, timedelta

# ------------------- Command Handlers -------------------
async def start(update: Update, context: CallbackContext):
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
        "Track activity across all groups\\! 🎀📊\n\n"
        f"🆕 New Features Added\\!\n"
        f"• Global Leaderboards\n• Profile Stats\n• Sudo Commands"
    )
    
    await update.message.reply_photo(
        photo="https://telegra.ph/file/28e287f80fd6a7ba67d62.jpg",
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

# ------------------- /gstat Handler -------------------
async def gstat(update: Update, context: CallbackContext):
    msg = await update.message.reply_photo(
        photo="https://telegra.ph/file/382aff205e8cd367b824c.jpg",
        caption="🌸 Loading Group Leaderboard..."
    )
    await show_leaderboard(context, msg.chat_id, msg.message_id, is_today=True)

# ------------------- /topgroups Handler -------------------
async def top_groups(update: Update, context: CallbackContext):
    msg = await update.message.reply_photo(
        photo="https://telegra.ph/file/group_banner.jpg",
        caption="🌸 Loading Global Groups Leaderboard..."
    )
    await show_group_leaderboard(context, msg.chat_id, msg.message_id, is_today=True)

# ------------------- /topusers Handler -------------------
async def top_users(update: Update, context: CallbackContext):
    msg = await update.message.reply_photo(
        photo="https://telegra.ph/file/users_banner.jpg",
        caption="🌸 Loading Global Users Leaderboard..."
    )
    await show_global_leaderboard(context, msg.chat_id, msg.message_id, is_today=True)

# ------------------- /profile Handler -------------------
async def profile(update: Update, context: CallbackContext):
    user = update.effective_user
    chat = update.effective_chat
    
    # Current Group Stats
    group_stats = await db.overall_stats.find_one(
        {"user_id": user.id, "group_id": chat.id}
    )
    
    # Global Stats
    global_stats = await db.global_users.find_one({"user_id": user.id})
    
    profile_text = (
        f"🌸 *{await escape_markdown(user.first_name)}'s Profile* 🌸\n\n"
        f"📊 *Current Group Stats*\n"
        f"Messages: {group_stats.get('count', 0) if group_stats else 0}\n"
        f"🏆 *Global Stats*\n"
        f"Total: {global_stats.get('total', 0) if global_stats else 0}\n"
        f"Rank: #{await get_global_rank(user.id)}"
    )
    
    await update.message.reply_photo(
        photo=user.photo_url if user.photo else "https://telegra.ph/file/default_profile.jpg",
        caption=profile_text,
        parse_mode="MarkdownV2"
    )

# ------------------- /stats Handler -------------------
async def bot_stats(update: Update, context: CallbackContext):
    total_groups = await db.groups.count_documents({})
    total_users = await db.global_users.count_documents({})
    
    stats_text = (
        f"🤖 *Bot Statistics* 🤖\n\n"
        f"• Groups: {total_groups}\n"
        f"• Users: {total_users}\n"
        f"• Uptime: {await get_uptime()}"
    )
    
    await update.message.reply_photo(
        photo="https://telegra.ph/file/stats_banner.jpg",
        caption=stats_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]]),
        parse_mode="MarkdownV2"
    )
