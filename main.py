from pyrogram import idle

from init import logs, bot


if __name__ == "__main__":
    logs.info("连接服务器中。。。")
    bot.start()
    logs.info("运行成功！")
    idle()
    bot.stop()
