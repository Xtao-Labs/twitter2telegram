import asyncio
import traceback
from typing import List

from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from defs.glover import cid, tid, owner
from defs.models import User, Tweet
from init import bot, logs
from defs.sqlite import TweetDB, UserDB
from defs.feed import get_user, UsernameNotFound


def get_button(user: User, tweet: Tweet) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Source", url=tweet.url),
                InlineKeyboardButton("Author", url=user.link),
            ]
        ]
    )


def get_media_group(text: str, tweet: Tweet) -> List[InputMediaPhoto]:
    data = []
    images = tweet.images[:10]
    for idx, image in enumerate(images):
        data.append(
            InputMediaPhoto(
                image,
                caption=text if idx == 0 else None,
                parse_mode=ParseMode.HTML,
            )
        )
    return data


def flood_wait():
    def decorator(function):
        async def wrapper(*args, **kwargs):
            try:
                return await function(*args, **kwargs)
            except FloodWait as e:
                logs.warning(f"遇到 FloodWait，等待 {e.value} 秒后重试！")
                await asyncio.sleep(e.value + 1)
                return await wrapper(*args, **kwargs)
            except Exception as e:
                traceback.format_exc()
                raise e

        return wrapper

    return decorator


@flood_wait()
async def send_to_user(user: User, tweet: Tweet):
    text = "<b>Twitter Timeline Update</b>\n\n<code>"
    text += tweet.content
    text += f"</code>\n\n{user.format} 发表于 {tweet.time_str}"
    if not tweet.images:
        return await bot.send_message(
            cid,
            text,
            disable_web_page_preview=True,
            reply_to_message_id=tid,
            parse_mode=ParseMode.HTML,
            reply_markup=get_button(user, tweet),
        )
    elif len(tweet.images) == 1:
        return await bot.send_photo(
            cid,
            tweet.images[0],
            caption=text,
            reply_to_message_id=tid,
            parse_mode=ParseMode.HTML,
            reply_markup=get_button(user, tweet),
        )
    else:
        await bot.send_media_group(
            cid,
            get_media_group(text, tweet),
            reply_to_message_id=tid,
        )


@flood_wait()
async def send_username_changed(user: str):
    text = f"获取 {user} 的数据失败，可能用户名已改变，请考虑移除该用户"
    await bot.send_message(owner, text)


@flood_wait()
async def send_api_error():
    text = "获取数据过多，可能 API 失效"
    await bot.send_message(owner, text)


async def send_check(user_data: User):
    need_send_tweets = [
        tweet for tweet in user_data.tweets
        if not TweetDB.check_id(user_data.username, tweet.id)
    ]
    logs.info(f"需要推送 {len(need_send_tweets)} 条推文")
    for tweet in need_send_tweets:
        try:
            await send_to_user(user_data, tweet)
        except Exception:
            logs.error(f"推送 {user_data.name} 的推文 {tweet.id} 失败")
            traceback.print_exc()
        TweetDB.add(user_data.username, tweet.id)


async def check_update():
    logs.info("开始检查更新")
    users = UserDB.get_all()
    failed_users = []
    nums = len(users)
    for idx, user in enumerate(users):
        try:
            user_data = await get_user(user)
            if user_data:
                logs.info(f"获取 {user_data.name} 的数据成功，共 {len(user_data.tweets)} 条推文")
                await send_check(user_data)
            else:
                logs.warning(f"获取 {user} 的数据失败，未知原因")
                failed_users.append(user)
        except UsernameNotFound:
            logs.warning(f"获取 {user} 的数据失败，可能用户名已改变")
            failed_users.append(user)
        except Exception:
            traceback.print_exc()
        logs.info(f"处理完成，剩余 {nums - idx - 1} 个用户")
    if len(failed_users) > 5:
        logs.warning("失效数据过多，可能 API 失效")
        await send_api_error()
    else:
        for user in failed_users:
            await send_username_changed(user)
    logs.info("检查更新完成")
