# (c) Jigarvarma2005
# Please make pull request if something wrong
# Coded by noob
# Edit at your own risk
import os
from database import db
from pyrogram import Client, filters
from config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from logging.handlers import RotatingFileHandler


if os.path.exists("log.txt"):
    with open("log.txt", "r+") as f_d:
        f_d.truncate(0)

# the logging things
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "log.txt", maxBytes=50000000, backupCount=10
        ),
        logging.StreamHandler(),
    ],
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)


JV_BOT = Client("AntiChannelBot",
                api_id=Config.API_ID,
                api_hash=Config.API_HASH,
                bot_token=Config.BOT_TOKEN)


async def whitelist_check(chat_id,channel_id=0):
    if not (await db.is_chat_exist(chat_id)):
        await db.add_chat_list(chat_id)
    _chat_list = await db.get_chat_list(chat_id)
    if int(channel_id) in _chat_list:
        return True
    else:
        return False

async def get_channel_id_from_input(bot, message):
    try:
        a_id = message.text.split(" ",1)[1]
    except:
        await message.reply_text("Send cmd along with channel id")
        return False
    if not str(a_id).startswith("-"):
        try:
            a_id = await bot.get_chat(a_id)
            a_id = a_id.id
        except:
            await message.reply_text("Inavalid channel id")
            return False
    return a_id



custom_message_filter = filters.create(lambda _, __, message: False if message.forward_from_chat or message.from_user else True)
custom_chat_filter = filters.create(lambda _, __, message: True if message.sender_chat else False)

@JV_BOT.on_message(custom_message_filter & filters.group & custom_chat_filter)
async def main_handler(bot, message):
    chat_id = message.chat.id
    a_id = message.sender_chat.id
    if (await whitelist_check(chat_id, a_id)):
        return
    elif a_id is chat_id:
        pass
    else:
        return
    try:
        res = await bot.ban_chat_member(chat_id, a_id)
    except:
        return await message.reply_text("Promote me as admin, to use me")
    if res:
        mention = f"@{message.sender_chat.username}" if message.sender_chat.username else message.chat_data.title
        await message.reply_text(text=f"{mention} has been banned.\n\n💡 He can write only with his profile but not through other channels.",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Unban", callback_data=f"unban_{chat_id}_{a_id}")]]),
                              )
    await message.delete()


@JV_BOT.on_message(filters.command(["start"]) & filters.private)
async def start_handler(bot, message):
    await message.reply_text(text="""Hey! Just add me to the chat, and I will block the channels that write to the chat,

check /help for more.""",
                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Bots Channel", url=f"https://t.me/Universal_Projects"),
                                                                 InlineKeyboardButton("Support Group", url=f"https://t.me/JV_Community")]]),
                             disable_web_page_preview=True)

@JV_BOT.on_message(filters.command(["help"]) & filters.private)
async def help_handler(bot, message):
    await message.reply_text(text="""/ban [channel_id] : ban channel from sending message as channel.
/unban [channel_id] : unban channel from sending message as channel.
/add_whitelist [channel_id] : add channel into whitelist and protect channel for automatic actions.
/del_whitelist [channel_id] : remove channel from whitelist.
/show_whitelist : Show all white list channels.

for more help ask at @JV_Community""",
                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Bots Channel", url=f"https://t.me/Universal_Projects"),
                                                                 InlineKeyboardButton("Support Group", url=f"https://t.me/JV_Community")]]),
                             disable_web_page_preview=True)



@JV_BOT.on_callback_query()
async def cb_handler(bot, query):
    cb_data = query.data
    if cb_data.startswith("unban_"):
        an_id = cb_data.split("_")[-1]
        chat_id = cb_data.split("_")[-2]
        user = await bot.get_chat_member(chat_id, query.from_user.id)
        if user.status == "creator" or user.status == "administrator":
            pass
        elif message.sender_chat.id is chat_id:
            pass
        else:
            return await query.answer("This Message is Not For You!", show_alert=True)
        await bot.resolve_peer(an_id)
        res = await query.message.chat.unban_member(an_id)
        chat_data = await bot.get_chat(an_id)
        mention = f"@{chat_data.username}" if chat_data.username else chat_data.title
        if res:
            await query.message.reply_text(f"{mention} has been unbanned by {query.from_user.mention}")
            await query.message.edit_reply_markup(reply_markup=None)

@JV_BOT.on_message(filters.command(["ban"]) & filters.group)
async def cban_handler(bot, message):
    chat_id = message.chat.id
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator" or user.status == "administrator":
        pass
    elif message.sender_chat.id is chat_id:
        pass
    else:
        return
    try:
        a_id = await get_channel_id_from_input(bot, message)
        if not a_id:
            return
        if (await whitelist_check(chat_id, a_id)):
            return await message.reply_text("Channel Id found in whitelist, so you can't ban this channel")
        await bot.resolve_peer(a_id)
        res = await bot.ban_chat_member(chat_id, a_id)
        chat_data = await bot.get_chat(a_id)
        mention = f"@{chat_data.username}" if chat_data.username else chat_data.title
        if res:
            await message.reply_text(text=f"{mention} has been banned.\n\n💡 He can write only with his profile but not through other channels.",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Unban", callback_data=f"unban_{chat_id}_{a_id}")]]),
                              )
        else:
            await message.reply_text("Invalid Channel id, 💡check channel id")
    except Exception as e:
        print(e)

@JV_BOT.on_message(filters.command(["unban"]) & filters.group)
async def uncban_handler(bot, message):
    chat_id = message.chat.id
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    
    if user.status == "creator" or user.status == "administrator":
        pass
    else:
        return
    try:
        a_id = await get_channel_id_from_input(bot, message)
        if not a_id:
            return
        if (await whitelist_check(chat_id, a_id)):
            return
        await bot.resolve_peer(a_id)
        res = await message.chat.unban_member(a_id)
        chat_data = await bot.get_chat(a_id)
        mention = f"@{chat_data.username}" if chat_data.username else chat_data.title
        if res:
            await message.reply_text(text=f"{mention} has been unbanned by {message.from_user.mention}")
        else:
            await message.reply_text("Invalid Channel id, 💡check channel id")
    except Exception as e:
        print(e)
        await message.reply_text(e)


@JV_BOT.on_message(filters.command(["add_whitelist"]) & filters.group)
async def add_whitelist_handler(bot, message):
    chat_id = message.chat.id
    user = await bot.get_chat_member(chat_id, message.from_user.id)
    if user.status == "creator" or user.status == "administrator":
        pass
    elif message.sender_chat.id is chat_id:
        pass
    else:
        return
    try:
        a_id = await get_channel_id_from_input(bot, message)
        if not a_id:
            return
        if (await whitelist_check(chat_id, a_id)):
            return await message.reply_text("Channel Id already found in whitelist")
        chk,msg = await db.add_chat_list(chat_id, a_id)
        if chk and msg != "":
            await message.reply_text(msg)
        else:
            await message.reply_text("Something wrong happend")
    except Exception as e:
        print(e)


@JV_BOT.on_message(filters.command(["del_whitelist"]) & filters.group)
async def del_whitelist_handler(bot, message):
    chat_id = message.chat.id
    user = await bot.get_chat_member(chat_id, message.from_user.id)
    if user.status == "creator" or user.status == "administrator":
        pass
    elif message.sender_chat.id is chat_id:
        pass
    else:
        return
    try:
        a_id = await get_channel_id_from_input(bot, message)
        if not a_id:
            return
        if not (await whitelist_check(chat_id, a_id)):
            return await message.reply_text("Channel Id not found in whitelist")
        chk,msg = await db.del_chat_list(message.chat.id, a_id)
        if chk:
            await message.reply_text(msg)
        else:
            await message.reply_text("Something wrong happend")
    except Exception as e:
        print(e)


@JV_BOT.on_message(filters.command(["show_whitelist"]) & filters.group)
async def del_whitelist_handler(bot, message):
    chat_id = message.chat.id
    user = await bot.get_chat_member(chat_id, message.from_user.id)
    if user.status == "creator" or user.status == "administrator":
        pass
    elif message.sender_chat.id is chat_id:
        pass
    else:
        return
    show_wl = await db.get_chat_list(chat_id)
    if show_wl:
        await message.reply_text(f"This ids found in whitelist\n\n{show_wl}")
    else:
        await message.reply_text("White list not found.")

if __name__ == "__main__":
    JV_BOT.run()
