import pyrogram
import httpx

from defs.glover import api_id, api_hash, logtail_token
from scheduler import scheduler
from logging import getLogger, INFO, ERROR, StreamHandler, basicConfig, FileHandler, Formatter
from coloredlogs import ColoredFormatter
from logtail import LogtailHandler

# Enable logging
logs = getLogger("T2G")
logging_format = "%(levelname)s [%(asctime)s] [%(name)s] %(message)s"
logging_handler = StreamHandler()
logging_handler.setFormatter(ColoredFormatter(logging_format))
file_handler = FileHandler("log.txt", mode="w", encoding="utf-8")
file_handler.setFormatter(Formatter(logging_format))
logtail_handler = LogtailHandler(source_token=logtail_token)
root_logger = getLogger()
root_logger.setLevel(ERROR)
root_logger.addHandler(logging_handler)
root_logger.addHandler(file_handler)
if logtail_token:
    root_logger.addHandler(logtail_handler)
basicConfig(level=INFO)
logs.setLevel(INFO)

if not scheduler.running:
    scheduler.start()

bot = pyrogram.Client(
    "bot", api_id=api_id, api_hash=api_hash, plugins=dict(root="plugins")
)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.72 Safari/537.36"
}
request = httpx.AsyncClient(timeout=60.0, headers=headers)
