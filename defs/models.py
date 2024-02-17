from datetime import datetime, timedelta
from typing import List

from pydantic import BaseModel
from httpx import URL


class Tweet(BaseModel):
    content: str
    old_url: str
    time: datetime
    images: List[str]

    @property
    def id(self) -> int:
        tid = self.url.split("/")[-1].replace("#m", "")
        return int(tid)

    @property
    def time_str(self) -> str:
        utc_8_time = self.time + timedelta(hours=8)
        return utc_8_time.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def url(self) -> str:
        u = URL(self.old_url)
        return self.old_url.replace(u.host, "twitter.com")


class User(BaseModel):
    username: str
    name: str
    tweets: List[Tweet]

    @property
    def link(self) -> str:
        return f"https://twitter.com/{self.username}"

    @property
    def format(self) -> str:
        return f'<a href="{self.link}">{self.name}</a>'
