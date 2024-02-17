import traceback
from asyncio import Lock
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup

from init import request
from defs.glover import rss_hub_host, nitter_host
from defs.models import Tweet, User
from feedparser import parse, FeedParserDict

LOCK = Lock()


class UsernameNotFound(Exception):
    pass


class HostNeedChange(Exception):
    pass


def retry(func):
    async def wrapper(*args, **kwargs):
        for i in range(3):
            try:
                return await func(*args, **kwargs)
            except HostNeedChange:
                if i == 2:
                    raise HostNeedChange
                continue

    return wrapper


@retry
async def rsshub_get(username: str, host: str) -> Optional[FeedParserDict]:
    url = f"{host}/twitter/user/{username}"
    response = await request.get(url)
    if response.status_code == 200:
        return parse(response.text)
    elif response.status_code == 404:
        raise UsernameNotFound
    raise HostNeedChange


@retry
async def nitter_get(username: str, host: str) -> Optional[FeedParserDict]:
    url = f"{host}/{username}/rss"
    async with LOCK:
        response = await request.get(url)
    if response.status_code == 200:
        return parse(response.text)
    elif response.status_code == 404:
        raise UsernameNotFound
    raise HostNeedChange


async def parse_tweets(data: List[FeedParserDict]) -> List[Tweet]:
    tweets = []
    for tweet in data:
        try:
            description = tweet.get("description", "")
            soup = BeautifulSoup(description, "lxml")
            content = soup.get_text()
            img_tag = soup.find_all("img")
            images = [img.get("src") for img in img_tag if img.get("src")]
            url = tweet.get("link", "")
            time = datetime.strptime(tweet.get("published", ""), "%a, %d %b %Y %H:%M:%S %Z")
            tweets.append(
                Tweet(
                    content=content,
                    old_url=url,
                    time=time,
                    images=images
                )
            )
        except Exception:
            traceback.print_exc()
    return tweets


async def parse_user(username: str, data: FeedParserDict) -> User:
    title = data.get("feed", {}).get("title", "")
    name = title.replace("Twitter @", "")
    tweets = await parse_tweets(data.get("entries", []))
    return User(username=username, name=name, tweets=tweets)


async def get_user(username: str) -> Optional[User]:
    data = None
    try:
        data = await get_user_rsshub(username)
    except HostNeedChange:
        pass
    if not data:
        try:
            data = await get_user_nitter(username)
        except HostNeedChange:
            raise UsernameNotFound
    return data


async def get_user_rsshub(username: str) -> Optional[User]:
    for host in rss_hub_host:
        try:
            data = await rsshub_get(username, host)
            if data:
                return await parse_user(username, data)
        except HostNeedChange:
            if host == rss_hub_host[-1]:
                raise HostNeedChange
            continue
    return None


async def get_user_nitter(username: str) -> Optional[User]:
    for host in nitter_host:
        try:
            data = await nitter_get(username, host)
            if data:
                return await parse_user(username, data)
        except HostNeedChange:
            if host == nitter_host[-1]:
                raise HostNeedChange
            continue
    return None
