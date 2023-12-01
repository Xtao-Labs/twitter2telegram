from pyrogram.types import Message

from defs.glover import owner
from init import bot
from scheduler import scheduler

from pyrogram import filters

from defs.update import check_update


@bot.on_message(filters=filters.command("check_update") & filters.user(owner))
async def update_all(_, message: Message):
    msg = await message.reply("开始检查更新！")
    await check_update()
    await msg.edit("检查更新完毕！")


@scheduler.scheduled_job("cron", minute="*/15", id="update_all")
async def update_all_30_minutes():
    await check_update()
