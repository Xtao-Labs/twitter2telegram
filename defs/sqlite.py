from pathlib import Path
from typing import List

from sqlitedict import SqliteDict

data_path = Path("data")
data_path.mkdir(exist_ok=True)
db_path = data_path / "data.db"
db = SqliteDict(db_path, autocommit=True)


class TweetDB:
    prefix = "tweet_"

    @staticmethod
    def get_all(username: str) -> List[int]:
        return db.get(f"{TweetDB.prefix}{username}", [])

    @staticmethod
    def check_id(username: str, tid: int) -> bool:
        return tid in TweetDB.get_all(username)

    @staticmethod
    def add(username: str, tid: int) -> None:
        tweets = TweetDB.get_all(username)
        tweets.append(tid)
        db[f"{TweetDB.prefix}{username}"] = tweets


class UserDB:
    @staticmethod
    def get_all() -> List[str]:
        return db.get("users", [])

    @staticmethod
    def check(username: str) -> bool:
        return username in UserDB.get_all()

    @staticmethod
    def add(username: str) -> None:
        users = UserDB.get_all()
        users.append(username)
        db["users"] = users

    @staticmethod
    def remove(username: str) -> None:
        users = UserDB.get_all()
        users.remove(username)
        db["users"] = users
