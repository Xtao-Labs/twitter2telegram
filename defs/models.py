from datetime import datetime, timedelta
from typing import List

from pydantic import BaseModel


class Tweet(BaseModel):
    content: str
    url: str
    time: datetime
    images: List[str]

    @property
    def id(self) -> int:
        return int(self.url.split("/")[-1])

    @property
    def time_str(self) -> str:
        utc_8_time = self.time + timedelta(hours=8)
        return utc_8_time.strftime("%Y-%m-%d %H:%M:%S")


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
