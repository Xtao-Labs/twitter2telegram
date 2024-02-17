from asyncio import Lock

from pyrogram.types import Message

from defs.glover import owner
from init import bot
from scheduler import scheduler

from pyrogram import filters

from defs.update import check_update

_lock = Lock()


@bot.on_message(filters=filters.command("check_update") & filters.user(owner))
async def update_all(_, message: Message):
    if _lock.locked():
        await message.reply("正在检查更新，请稍后再试！")
        return
    async with _lock:
        msg = await message.reply("开始检查更新！")
        await check_update()
        await msg.edit("检查更新完毕！")


@scheduler.scheduled_job("cron", hour="*", minute="0", id="update_all")
async def update_all_60_minutes():
    if _lock.locked():
        return
    async with _lock:
        await check_update()
