from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import db
from utils import *
import re

# ------------------- /broadcast Handler -------------------
async def broadcast(update: Update, context: CallbackContext):
    if not await is_sudo(update.effective_user.id):
        await update.message.reply_text("❌ Permission Denied!")
        return

    args = context.args
    message = " ".join([arg for arg in args if not arg.startswith("-")])
    flags = [arg.lower() for arg in args if arg.startswith("-")]

    # Collect targets
    groups = await db.groups.distinct("_id") if "-user" not in flags else []
    users = await db.global_users.distinct("user_id") if "-group" not in flags else []

    success = 0
    pinned = 0
    
    # Send to groups
    for group_id in groups:
        try:
            msg = await context.bot.send_message(group_id, message)
            if "-pin" in flags:
                await context.bot.pin_chat_message(group_id, msg.message_id)
                pinned += 1
            success += 1
        except Exception as e:
            print(f"Broadcast Error in {group_id}: {e}")

    # Send to users
    for user_id in users:
        try:
            await context.bot.send_message(user_id, message)
            success += 1
        except Exception as e:
            print(f"Broadcast Error to {user_id}: {e}")

    # Result message
    result_text = (
        f"📢 Broadcast Results:\n"
        f"• Success: {success}\n"
        f"• Groups: {len(groups)}\n"
        f"• Users: {len(users)}\n"
        f"• Pinned: {pinned}"
    )
    await update.message.reply_text(result_text)

# ------------------- Sudo Management -------------------
async def add_sudo(update: Update, context: CallbackContext):
    if update.effective_user.id != int(os.getenv("OWNER_ID")):
        return
    
    target_user = update.message.reply_to_message.from_user
    await db.sudo_users.update_one(
        {"user_id": target_user.id},
        {"$set": {"username": target_user.username}},
        upsert=True
    )
    await update.message.reply_text(f"✅ Added @{target_user.username} to sudo!")

async def sudolist(update: Update, context: CallbackContext):
    sudo_users = await db.sudo_users.find().to_list(None)
    text = "👑 Sudo Users:\n" + "\n".join(
        [f"• {u['username']} ({u['user_id']})" for u in sudo_users]
    )
    await update.message.reply_text(text)
