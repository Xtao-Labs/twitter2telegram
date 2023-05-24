from init import bot

from pyrogram import filters


@bot.on_message(filters=filters.command("ping"))
async def ping(_, message):
    await message.reply("pong")
