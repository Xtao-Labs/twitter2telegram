import re

from pyrogram import filters
from pyrogram.types import Message

from defs.feed import get_user
from init import bot

from defs.sqlite import UserDB
from defs.glover import owner


async def check_user(username: str) -> bool:
    try:
        await get_user(username)
        return True
    except:
        return False


@bot.on_message(filters=filters.command("add_user") & filters.user(owner))
async def add_user(_, message: Message):
    try:
        username = message.text.split(" ")[1]
    except IndexError:
        await message.reply("请指定用户名！")
        return
    if UserDB.check(username):
        await message.reply("该用户添加过了！")
        return
    if not await check_user(username):
        await message.reply("该用户不存在！或者 rss 服务出现问题！")
        return
    UserDB.add(username)
    await message.reply("添加成功！")


@bot.on_message(filters=filters.regex(r"https://twitter.com/(.*)") & filters.chat(owner))
async def add_user_regex(_, message: Message):
    try:
        username = re.findall(r"https://twitter.com/(.*)", message.text)[0]
        if not username:
            raise IndexError
    except IndexError:
        await message.reply("请指定用户名！")
        return
    if UserDB.check(username):
        await message.reply("该用户添加过了！")
        return
    if not await check_user(username):
        await message.reply("该用户不存在！或者 rss 服务出现问题！")
        return
    UserDB.add(username)
    await message.reply(f"添加 {username} 成功！")


@bot.on_message(filters=filters.command("del_user") & filters.user(owner))
async def del_user(_, message: Message):
    try:
        username = message.text.split(" ")[1]
    except IndexError:
        await message.reply("请指定用户名！")
        return
    if not UserDB.check(username):
        await message.reply("该用户未添加！")
        return
    UserDB.remove(username)
    await message.reply(f"删除 {username} 成功！")


@bot.on_message(filters=filters.command("list_user") & filters.user(owner))
async def list_user(_, message: Message):
    users = UserDB.get_all()
    if not users:
        await message.reply("列表为空！")
        return

    def format_user(username: str):
        return f'<a href="https://twitter.com/{username}">{username}</a>'

    text = "\n".join([format_user(user) for user in users])
    await message.reply(f"用户列表：\n{text}")
