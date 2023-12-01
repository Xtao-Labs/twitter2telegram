import asyncio
import time
from typing import List

from defs.feed import UsernameNotFound
from defs.models import User
from defs.sqlite import UserDB, TweetDB
from defs.update import async_get_user
from init import logs


async def get_data(tasks):
    tasks_count = len(tasks) // 20 + 1 if len(tasks) % 20 else len(tasks) // 20
    start_time = time.time()
    for idx in range(0, len(tasks), 20):
        tasks_group = tasks[idx:idx + 20]
        logs.info(f"开始获取第 {idx // 20 + 1} / {tasks_count} 组用户的数据")
        await asyncio.gather(*tasks_group)
    logs.info(f"获取数据用时 {time.time() - start_time:.2f} 秒")


async def get_need_update_usernames():
    with open("export.txt", "r", encoding="utf-8") as f:
        usernames: List[str] = [i for i in f.read().strip().split("\n") if i]
    users = UserDB.get_all()
    for i in usernames.copy():
        if i in users:
            usernames.remove(i)
    return usernames


async def check_need_add(users_data) -> List[str]:
    nums = len(users_data)
    keys = list(users_data.keys())
    values = list(users_data.values())
    need_add = []
    for idx in range(nums):
        username = keys[idx]
        user_data = values[idx]
        if isinstance(user_data, User):
            logs.info(f"获取 {user_data.name} (@{user_data.username}) 的数据成功，"
                      f"共 {len(user_data.tweets)} 条推文")
            need_send_tweets = [
                tweet for tweet in user_data.tweets[1:]
                if not TweetDB.check_id(user_data.username, tweet.id)
            ]
            for tweet in need_send_tweets:
                TweetDB.add(user_data.username, tweet.id)
            need_add.append(user_data.username)
        elif isinstance(user_data, UsernameNotFound):
            logs.warning(f"获取 {username} 的数据失败，可能用户名已改变")
    return need_add


async def start_import():
    logs.info("开始批量导入用户")
    users = await get_need_update_usernames()
    if not users:
        logs.info("没有需要导入的用户")
        return
    logs.info(f"共有 {len(users)} 个用户需要导入")
    users_data = {user: None for user in users}
    tasks = [async_get_user(users_data, user) for user in users]
    await get_data(tasks)
    need_add = await check_need_add(users_data)
    if not need_add:
        logs.info("没有需要导入的用户")
        return
    for i in need_add:
        UserDB.add(i)
    logs.info(f"导入 {len(need_add)} 个用户完成")


if __name__ == '__main__':
    asyncio.run(start_import())
