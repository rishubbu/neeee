import os
from pyrogram import *
from pyrogram.types import *
from logging import getLogger
from ShrutiMusic import LOGGER, app
from ShrutiMusic.utils.database import db

try:
    wlcm = db.welcome
except:
    from ShrutiMusic.utils.database import welcome as wlcm

LOGGER = getLogger(__name__)

class temp:
    MELCOW = {}

# ✅ /welcome Command
@app.on_message(filters.command("welcome") & ~filters.private)
async def auto_state(_, message):
    usage = "✨ **Usage:** /welcome [on|off]"
    if len(message.command) == 1:
        return await message.reply_text(usage)

    chat_id = message.chat.id
    user = await app.get_chat_member(message.chat.id, message.from_user.id)

    if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        A = await wlcm.find_one({"chat_id": chat_id})
        state = message.text.split(None, 1)[1].strip().lower()

        if state == "on":
            if A and not A.get("disabled", False):
                return await message.reply_text("✅ Special Welcome is already **enabled**")
            await wlcm.update_one({"chat_id": chat_id}, {"$set": {"disabled": False}}, upsert=True)
            await message.reply_text("🎉 Special Welcome **Enabled** in this group!")

        elif state == "off":
            if A and A.get("disabled", False):
                return await message.reply_text("❌ Special Welcome is already **disabled**")
            await wlcm.update_one({"chat_id": chat_id}, {"$set": {"disabled": True}}, upsert=True)
            await message.reply_text("🚫 Special Welcome **Disabled** in this group!")

        else:
            await message.reply_text(usage)
    else:
        await message.reply("⚠️ Only Admins can use this command.")

# ✅ Modern Stylish Text Welcome
@app.on_chat_member_updated(filters.group, group=-3)
async def greet_group(_, member: ChatMemberUpdated):
    chat_id = member.chat.id
    A = await wlcm.find_one({"chat_id": chat_id})

    if A and A.get("disabled", False):
        return

    if (
        not member.new_chat_member
        or member.new_chat_member.status in {"banned", "left", "restricted"}
        or member.old_chat_member
    ):
        return

    user = member.new_chat_member.user if member.new_chat_member else member.from_user

    if (temp.MELCOW).get(f"welcome-{member.chat.id}") is not None:
        try:
            await temp.MELCOW[f"welcome-{member.chat.id}"].delete()
        except Exception as e:
            LOGGER.error(e)

    try:
        temp.MELCOW[f"welcome-{member.chat.id}"] = await app.send_message(
            member.chat.id,
            f"""
🌌✨ ━━━━━━━━━━━━━━━━━━ ✨🌌  

💎 <b>Welcome {user.mention}!</b> 💎  

🚀 <i>A new star just joined our galaxy!</i>  

🎶 Enjoy the vibes, make new friends,  
and let’s create unforgettable memories together.  

⚡ <b>Group:</b> {member.chat.title}  
💫 <b>Powered by:</b> <a href="https://t.me/{app.username}?start=help">{app.username}</a>  

🌌✨ ━━━━━━━━━━━━━━━━━━ ✨🌌
""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{app.username}?startgroup=True")]
            ]),
        )

    except Exception as e:
        LOGGER.error(e)