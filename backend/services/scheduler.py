import os

from apscheduler.schedulers.background import BackgroundScheduler

from services.job_fetcher import run_fetch

scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        run_fetch,
        "cron",
        hour=int(os.getenv("SCHEDULER_HOUR", "8")),
        minute=int(os.getenv("SCHEDULER_MINUTE", "0")),
        id="daily_job_fetch",
        replace_existing=True,
    )
    scheduler.start()
