from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone="Asia/ShangHai")
if not scheduler.running:
    scheduler.start()
