import os
from unidecode import unidecode
from PIL import ImageDraw, Image, ImageFont, Image
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

# ✅ Modern Stylish Welcome Card (without profile photo)
def welcomepic(user, chat, id, uname):
    # Base background
    background = Image.open("ShrutiMusic/assets/welcome.png").convert("RGBA")
    draw = ImageDraw.Draw(background)

    # Fonts
    font_big = ImageFont.truetype("ShrutiMusic/assets/font.ttf", size=95)
    font_med = ImageFont.truetype("ShrutiMusic/assets/font.ttf", size=55)
    font_small = ImageFont.truetype("ShrutiMusic/assets/font.ttf", size=45)

    # Modern Gradient Style Text
    def draw_shadow_text(position, text, font, fill="white"):
        x, y = position
        draw.text((x+3, y+3), text, font=font, fill="black")  # shadow
        draw.text(position, text, font=font, fill=fill)

    # Main Welcome Title
    draw_shadow_text((180, 160), f"✨ Welcome ✨", font_big, fill="#FFD700")

    # User Info
    draw_shadow_text((100, 300), f"👤 Name: {unidecode(user)}", font_med, fill="#00E5FF")
    draw_shadow_text((100, 380), f"🔖 Username: @{uname if uname else 'Not Set'}", font_med, fill="#ADFF2F")
    draw_shadow_text((100, 460), f"🆔 User ID: {id}", font_med, fill="#FF69B4")
    draw_shadow_text((100, 540), f"🏡 Group: {chat}", font_med, fill="#FFA500")

    # Footer
    draw_shadow_text((200, 680), "🎵 Enjoy the best music experience 🎵", font_small, fill="#FFFFFF")

    path = f"downloads/welcome#{id}.png"
    background.save(path)
    return path

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

# ✅ Special Welcome
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
        welcomeimg = welcomepic(
            user.first_name, member.chat.title, user.id, user.username
        )
        temp.MELCOW[f"welcome-{member.chat.id}"] = await app.send_photo(
            member.chat.id,
            photo=welcomeimg,
            caption=f"""
🌸✨ ──────────────── ✨🌸

<b>🎊 Welcome {user.mention} 🎊</b>

🏡 Group : <b>{member.chat.title}</b>  
🆔 User ID : <code>{user.id}</code>  
🔖 Username : @{user.username if user.username else "Not Set"}  

━━━━━━━━━━━━━━━━━━━━━━━  
💖 <b>We’re so happy to have you here!</b>  
🎵 Enjoy the best music experience 🎵  

<blockquote>⚡ Powered by ➤ <a href="https://t.me/{app.username}?start=help">ShrutiMusic</a></blockquote>
🌸✨ ──────────────── ✨🌸
""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{app.username}?startgroup=True")]
            ]),
        )

    except Exception as e:
        LOGGER.error(e)

    try:
        os.remove(f"downloads/welcome#{user.id}.png")
    except Exception:
        pass