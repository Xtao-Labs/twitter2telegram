import traceback
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup

from init import request
from defs.glover import rss_hub_host
from defs.models import Tweet, User
from feedparser import parse, FeedParserDict


class UsernameNotFound(Exception):
    pass


class HostNeedChange(Exception):
    pass


async def get(username: str, host: str) -> Optional[FeedParserDict]:
    url = f"{host}/twitter/user/{username}"
    response = await request.get(url)
    if response.status_code == 200:
        return parse(response.text)
    elif response.status_code == 404:
        raise HostNeedChange
    else:
        return None


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
                    url=url,
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
    for host in rss_hub_host:
        try:
            data = await get(username, host)
            if data:
                return await parse_user(username, data)
        except HostNeedChange:
            if host == rss_hub_host[-1]:
                raise UsernameNotFound
            continue
    return None
